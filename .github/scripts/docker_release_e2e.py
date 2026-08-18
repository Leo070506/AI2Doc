"""Run the release-gate HTTP and DOCX checks through the Compose frontend."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from xml.etree import ElementTree


BASE_URL = os.environ.get("AI2DOC_E2E_BASE_URL", "http://localhost:8080").rstrip("/")
INPUT_PATH = Path(os.environ.get("AI2DOC_E2E_INPUT", "examples/docker-release-example.md"))
ARTIFACT_DIR = Path(os.environ.get("AI2DOC_E2E_ARTIFACT_DIR", "validation-artifacts"))
OUTPUT_PATH = ARTIFACT_DIR / "AI2Doc_Docker_Test.docx"
RESULT_PATH = ARTIFACT_DIR / "e2e-result.json"


def fetch(request: urllib.request.Request, *, timeout: int = 30) -> tuple[int, bytes]:
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status, response.read()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    markdown = INPUT_PATH.read_text(encoding="utf-8")

    page_status, page_body = fetch(urllib.request.Request(f"{BASE_URL}/"))
    page_text = page_body.decode("utf-8")
    require(page_status == 200, f"Frontend returned HTTP {page_status}")
    require("AI2Doc" in page_text, "Frontend page does not contain AI2Doc")

    payload = json.dumps(
        {"content": markdown, "template": "academic"}, ensure_ascii=False
    ).encode("utf-8")
    convert_request = urllib.request.Request(
        f"{BASE_URL}/api/convert",
        data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    convert_status, convert_body = fetch(convert_request, timeout=60)
    response = json.loads(convert_body.decode("utf-8"))
    require(convert_status == 200, f"Conversion returned HTTP {convert_status}")
    require(response.get("status") == "success", "Conversion status is not success")
    require(isinstance(response.get("file"), str), "Download URL is missing")

    download_url = urllib.parse.urljoin(f"{BASE_URL}/", response["file"])
    download_status, document_bytes = fetch(
        urllib.request.Request(download_url), timeout=60
    )
    require(download_status == 200, f"Download returned HTTP {download_status}")
    require(document_bytes.startswith(b"PK"), "Downloaded file is not a DOCX ZIP")
    OUTPUT_PATH.write_bytes(document_bytes)

    second_download_status = None
    try:
        fetch(urllib.request.Request(download_url), timeout=30)
    except urllib.error.HTTPError as error:
        second_download_status = error.code
    require(second_download_status == 404, "Download token was not one-time")

    with zipfile.ZipFile(OUTPUT_PATH) as document:
        names = set(document.namelist())
        require("word/document.xml" in names, "DOCX is missing word/document.xml")
        require("word/styles.xml" in names, "DOCX is missing word/styles.xml")
        require(document.testzip() is None, "DOCX ZIP contains a corrupt member")

        document_xml = document.read("word/document.xml")
        root = ElementTree.fromstring(document_xml)
        visible_text = "".join(root.itertext())
        require("AI2Doc Docker Test" in visible_text, "Title is missing from DOCX")
        require("这是一个Docker环境测试。" in visible_text, "Chinese text is missing")
        require("Docker" in visible_text and "DOCX" in visible_text, "Table text is missing")
        require(b"<m:oMath" in document_xml, "Native OMML formula is missing")
        require(b"<w:tbl" in document_xml, "Word table is missing")

        headers = sorted(name for name in names if name.startswith("word/header"))
        footers = sorted(name for name in names if name.startswith("word/footer"))
        require(headers, "Academic template header was not applied")
        require(footers, "Academic template footer was not applied")

    result = {
        "base_url": BASE_URL,
        "template": "academic",
        "frontend_http": page_status,
        "conversion_http": convert_status,
        "download_http": download_status,
        "second_download_http": second_download_status,
        "output_file": str(OUTPUT_PATH),
        "output_bytes": len(document_bytes),
        "docx_zip_valid": True,
        "chinese_text": True,
        "native_omml": True,
        "word_table": True,
        "academic_header": headers,
        "academic_footer": footers,
    }
    RESULT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:  # noqa: BLE001 - release gate must print the cause
        print(f"docker-release-e2e: FAILED: {error}", file=sys.stderr)
        raise
