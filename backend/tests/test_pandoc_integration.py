from __future__ import annotations

import os
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import pytest
from fastapi.testclient import TestClient

from app.config import PROJECT_DIR, Settings
from app.main import create_app
from app.services.pandoc import PandocRunner

WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
MATH_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"


def find_pandoc() -> str | None:
    configured = os.getenv("AI2DOC_PANDOC_PATH")
    if configured and Path(configured).is_file():
        return configured
    portable = PROJECT_DIR / ".tools" / "pandoc-3.9.0.2" / "pandoc-3.9.0.2" / "pandoc.exe"
    if portable.is_file():
        return str(portable)
    return shutil.which("pandoc")


@pytest.fixture
def runner(tmp_path: Path) -> PandocRunner:
    executable = find_pandoc()
    if not executable:
        pytest.skip("Pandoc is not installed")
    return PandocRunner(
        Settings(
            pandoc_path=executable,
            templates_root=PROJECT_DIR / "templates",
            storage_root=tmp_path / "storage",
        )
    )


def convert(runner: PandocRunner, tmp_path: Path, markdown: str, template: str) -> Path:
    source = tmp_path / f"{template}.md"
    output = tmp_path / f"{template}.docx"
    source.write_text(markdown, encoding="utf-8")
    runner.convert(source, output, PROJECT_DIR / "templates" / template / "template.docx")
    return output


def document_root(path: Path):
    with zipfile.ZipFile(path) as archive:
        return ElementTree.fromstring(archive.read("word/document.xml")), archive.namelist()


def test_basic_markdown_and_chinese(runner: PandocRunner, tmp_path: Path) -> None:
    output = convert(
        runner,
        tmp_path,
        "# 人工智能报告\n\n- 深度学习\n- 自然语言处理\n\n| 技术 | 状态 |\n|---|---|\n| NLP | 正常 |",
        "report",
    )
    root, _ = document_root(output)
    text = "".join(node.text or "" for node in root.iter(f"{{{WORD_NS}}}t"))
    assert "人工智能报告" in text
    assert "自然语言处理" in text
    assert root.find(f".//{{{WORD_NS}}}tbl") is not None


def test_math_is_native_omml_not_an_image(runner: PandocRunner, tmp_path: Path) -> None:
    output = convert(
        runner,
        tmp_path,
        "# Formula\n\n$E=mc^2$\n\n$$\n\\frac{-b\\pm\\sqrt{b^2-4ac}}{2a}\n$$",
        "academic",
    )
    root, names = document_root(output)
    assert len(root.findall(f".//{{{MATH_NS}}}oMath")) >= 2
    assert root.find(f".//{{{DRAWING_NS}}}inline") is None
    assert not any(name.startswith("word/media/") for name in names)


@pytest.mark.parametrize(
    ("template", "header_text"),
    [
        ("academic", "AI2Doc Academic | Research &amp; Analysis"),
        ("report", "AI2Doc Report | Business Brief"),
        ("notes", "AI2Doc Notes | Learning Notes"),
    ],
)
def test_reference_templates_apply(
    runner: PandocRunner,
    tmp_path: Path,
    template: str,
    header_text: str,
) -> None:
    output = convert(runner, tmp_path, "# Template Test\n\nBody", template)
    with zipfile.ZipFile(output) as archive:
        headers = "".join(
            archive.read(name).decode("utf-8")
            for name in archive.namelist()
            if name.startswith("word/header") and name.endswith(".xml")
        )
    assert header_text in headers


def test_full_api_flow_with_real_pandoc(tmp_path: Path) -> None:
    executable = find_pandoc()
    if not executable:
        pytest.skip("Pandoc is not installed")
    settings = Settings(
        pandoc_path=executable,
        templates_root=PROJECT_DIR / "templates",
        storage_root=tmp_path / "api-storage",
        cleanup_interval_seconds=3600,
    )
    with TestClient(create_app(settings)) as client:
        created = client.post(
            "/api/convert",
            json={
                "content": "# AI 报告\n\n中文段落。\n\n$E=mc^2$\n\n| 项目 | 状态 |\n|---|---|\n| DOCX | 正常 |",
                "template": "notes",
            },
        )
        assert created.status_code == 200
        downloaded = client.get(created.json()["file"])

    assert downloaded.status_code == 200
    output = tmp_path / "downloaded.docx"
    output.write_bytes(downloaded.content)
    root, _ = document_root(output)
    text = "".join(node.text or "" for node in root.iter(f"{{{WORD_NS}}}t"))
    assert "AI 报告" in text
    assert root.find(f".//{{{MATH_NS}}}oMath") is not None
    assert root.find(f".//{{{WORD_NS}}}tbl") is not None
    assert not any(settings.storage_root.iterdir())


@pytest.mark.parametrize(
    ("example", "template", "expected_text"),
    [
        ("math-example.md", "academic", "Mathematical Formula Example"),
        ("report-example.md", "report", "AI Adoption Readiness Brief"),
        ("chinese-example.md", "notes", "人工智能项目周报"),
    ],
)
def test_public_examples_convert(
    runner: PandocRunner,
    tmp_path: Path,
    example: str,
    template: str,
    expected_text: str,
) -> None:
    markdown = (PROJECT_DIR / "examples" / example).read_text(encoding="utf-8")
    output = convert(runner, tmp_path, markdown, template)
    root, _ = document_root(output)
    text = "".join(node.text or "" for node in root.iter(f"{{{WORD_NS}}}t"))
    assert expected_text in text
