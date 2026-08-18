from __future__ import annotations

import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from conftest import FakePandocRunner


def test_json_conversion_and_one_time_download(client: TestClient) -> None:
    response = client.post(
        "/api/convert",
        json={"content": "# Report\n\n- One\n- Two", "template": "report"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert payload["filename"] == "AI2Doc_Report.docx"

    download = client.get(payload["file"])
    assert download.status_code == 200
    assert download.content.startswith(b"PK")
    assert "AI2Doc_Report.docx" in download.headers["content-disposition"]
    assert download.headers["cache-control"] == "private, no-store"
    assert download.headers["x-content-type-options"] == "nosniff"
    assert client.get(payload["file"]).status_code == 404


def test_markdown_upload(client: TestClient) -> None:
    response = client.post(
        "/api/convert",
        data={"template": "academic"},
        files={"file": ("answer.md", "# 中文\n\n人工智能", "text/markdown")},
    )
    assert response.status_code == 200


def test_rejects_large_content(client: TestClient) -> None:
    response = client.post(
        "/api/convert",
        json={"content": "x" * 1025, "template": "notes"},
    )
    assert response.status_code == 413
    assert response.json()["error"]["message"] == "File too large"


def test_rejects_invalid_template(client: TestClient) -> None:
    response = client.post(
        "/api/convert",
        json={"content": "# Test", "template": "unknown"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_template"


def test_rejects_non_markdown_upload(client: TestClient) -> None:
    response = client.post(
        "/api/convert",
        data={"template": "notes"},
        files={"file": ("answer.txt", "hello", "text/plain")},
    )
    assert response.status_code == 415


def test_rejects_non_utf8_markdown(client: TestClient) -> None:
    response = client.post(
        "/api/convert",
        data={"template": "notes"},
        files={"file": ("answer.md", b"\xff\xfe\x00", "text/markdown")},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_encoding"


def test_rejects_empty_content(client: TestClient) -> None:
    response = client.post(
        "/api/convert",
        json={"content": "\n  \n", "template": "report"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "empty_content"


def test_pandoc_unavailable(settings) -> None:
    with TestClient(create_app(settings, FakePandocRunner(available=False))) as client:
        response = client.post(
            "/api/convert",
            json={"content": "# Test", "template": "notes"},
        )
    assert response.status_code == 503
    assert response.json()["error"]["message"] == "Pandoc unavailable"


def test_conversion_failure_removes_workspace(settings) -> None:
    with TestClient(create_app(settings, FakePandocRunner(should_fail=True))) as client:
        response = client.post(
            "/api/convert",
            json={"content": "# Test", "template": "notes"},
        )
    assert response.status_code == 500
    assert response.json()["error"]["message"] == "Conversion failed"
    assert not any(settings.storage_root.iterdir())


def test_download_cleanup_removes_workspace(client: TestClient, settings) -> None:
    response = client.post(
        "/api/convert",
        json={"content": "# Test", "template": "notes"},
    )
    client.get(response.json()["file"])
    assert not any(settings.storage_root.iterdir())


def test_health_and_openapi_contract(client: TestClient) -> None:
    assert client.get("/health/live").json() == {"status": "ok"}
    ready = client.get("/health/ready")
    assert ready.status_code == 200
    assert ready.json()["templates"] == ["academic", "notes", "report"]
    schema = client.get("/openapi.json").json()
    assert {"application/json", "multipart/form-data"} <= set(
        schema["paths"]["/api/convert"]["post"]["requestBody"]["content"]
    )
