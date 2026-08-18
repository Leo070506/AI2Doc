from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import PROJECT_DIR, Settings
from app.errors import InvalidTemplateError
from app.services.pandoc import PandocRunner
from app.templates.catalog import resolve_template


@pytest.mark.parametrize("template", ["../report", "..\\report", "/tmp/report", "academic/../../report"])
def test_template_path_traversal_is_rejected(settings: Settings, template: str) -> None:
    with pytest.raises(InvalidTemplateError):
        resolve_template(settings, template)


def test_upload_filename_never_becomes_a_storage_path(
    client: TestClient,
    settings: Settings,
) -> None:
    response = client.post(
        "/api/convert",
        data={"template": "report"},
        files={"file": ("../../private-answer.md", "# Synthetic example", "text/markdown")},
    )
    assert response.status_code == 200
    stored_files = [path.name for path in settings.storage_root.rglob("*") if path.is_file()]
    assert stored_files == ["output.docx"]
    assert "private-answer.md" not in stored_files


def test_pandoc_uses_an_argument_array_without_a_shell(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "input.md"
    destination = tmp_path / "output.docx"
    source.write_text("# Safe content", encoding="utf-8")
    reference = PROJECT_DIR / "templates" / "report" / "template.docx"
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured.update(kwargs)
        output_arg = next(argument for argument in command if argument.startswith("--output="))
        output_path = Path(output_arg.removeprefix("--output="))
        with zipfile.ZipFile(output_path, "w") as archive:
            archive.writestr("[Content_Types].xml", "<Types/>")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("app.services.pandoc.subprocess.run", fake_run)
    runner = PandocRunner(
        Settings(
            pandoc_path="pandoc",
            templates_root=PROJECT_DIR / "templates",
            storage_root=tmp_path / "storage",
        )
    )
    monkeypatch.setattr(runner, "is_available", lambda: True)

    runner.convert(source, destination, reference)

    assert isinstance(captured["command"], list)
    assert captured["shell"] is False
    assert "--sandbox" in captured["command"]
    assert "# Safe content" not in captured["command"]
