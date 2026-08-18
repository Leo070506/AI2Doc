"""Markdown-to-DOCX use case orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.config import Settings
from app.errors import ConversionFailedError, FileTooLargeError
from app.services.files import DownloadArtifact, TemporaryFileStore
from app.services.markdown import clean_markdown
from app.services.pandoc import PandocRunner
from app.templates.catalog import resolve_template

DOWNLOAD_FILENAME = "AI2Doc_Report.docx"


@dataclass(slots=True)
class ConversionService:
    settings: Settings
    file_store: TemporaryFileStore
    pandoc_runner: PandocRunner

    def convert(self, content: str, template_name: str) -> DownloadArtifact:
        if len(content.encode("utf-8")) > self.settings.max_input_bytes:
            raise FileTooLargeError()

        cleaned = clean_markdown(content)
        reference_doc = resolve_template(self.settings, template_name)
        workspace = self.file_store.create_workspace()
        source = workspace / "input.md"
        destination = workspace / "output.docx"

        try:
            source.write_text(cleaned, encoding="utf-8", newline="\n")
            self.pandoc_runner.convert(source, destination, reference_doc)
            source.unlink(missing_ok=True)
            return self.file_store.register(destination, DOWNLOAD_FILENAME)
        except Exception:
            self.file_store.delete_workspace(workspace)
            raise
