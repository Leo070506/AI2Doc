"""Isolated Pandoc subprocess adapter."""

from __future__ import annotations

import shutil
import subprocess
import zipfile
from pathlib import Path

from app.config import Settings
from app.errors import ConversionFailedError, PandocUnavailableError


class PandocRunner:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def is_available(self) -> bool:
        executable = self.settings.pandoc_path
        if Path(executable).is_file():
            return True
        return shutil.which(executable) is not None

    def convert(self, source: Path, destination: Path, reference_doc: Path) -> None:
        if not self.is_available():
            raise PandocUnavailableError()

        command = [
            self.settings.pandoc_path,
            str(source),
            "--from=markdown+tex_math_dollars",
            "--to=docx",
            f"--reference-doc={reference_doc}",
            "--sandbox",
            f"--output={destination}",
        ]
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.settings.conversion_timeout_seconds,
                shell=False,
            )
        except FileNotFoundError as exc:
            raise PandocUnavailableError() from exc
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ConversionFailedError() from exc

        if completed.returncode != 0 or not destination.is_file():
            raise ConversionFailedError()
        if destination.stat().st_size > self.settings.max_output_bytes:
            raise ConversionFailedError()
        if not zipfile.is_zipfile(destination):
            raise ConversionFailedError()
