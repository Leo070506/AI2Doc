from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import PROJECT_DIR, Settings
from app.main import create_app


class FakePandocRunner:
    def __init__(self, available: bool = True, should_fail: bool = False) -> None:
        self.available = available
        self.should_fail = should_fail

    def is_available(self) -> bool:
        return self.available

    def convert(self, source: Path, destination: Path, reference_doc: Path) -> None:
        from app.errors import ConversionFailedError, PandocUnavailableError

        if not self.available:
            raise PandocUnavailableError()
        if self.should_fail:
            raise ConversionFailedError()
        with zipfile.ZipFile(destination, "w") as archive:
            archive.writestr("[Content_Types].xml", "<Types/>")
            archive.writestr("word/document.xml", source.read_text(encoding="utf-8"))


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(
        pandoc_path="pandoc",
        templates_root=PROJECT_DIR / "templates",
        storage_root=tmp_path / "storage",
        max_input_bytes=1024,
        max_output_bytes=10 * 1024 * 1024,
        conversion_timeout_seconds=30,
        file_ttl_seconds=3600,
        cleanup_interval_seconds=3600,
        cors_origins=("http://localhost:5173",),
    )


@pytest.fixture
def client(settings: Settings):
    with TestClient(create_app(settings, FakePandocRunner())) as test_client:
        yield test_client
