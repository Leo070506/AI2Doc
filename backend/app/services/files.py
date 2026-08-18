"""Short-lived, one-time download storage."""

from __future__ import annotations

import secrets
import shutil
import time
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.config import Settings
from app.errors import DownloadNotFoundError


@dataclass(frozen=True, slots=True)
class DownloadArtifact:
    token: str
    path: Path
    filename: str
    expires_at: datetime


class TemporaryFileStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._artifacts: dict[str, DownloadArtifact] = {}

    def ensure_storage(self) -> None:
        self.settings.storage_root.mkdir(parents=True, exist_ok=True)

    def create_workspace(self) -> Path:
        self.ensure_storage()
        workspace = self.settings.storage_root / secrets.token_urlsafe(24)
        workspace.mkdir(mode=0o700)
        return workspace

    def register(self, output_path: Path, filename: str) -> DownloadArtifact:
        token = secrets.token_urlsafe(32)
        artifact = DownloadArtifact(
            token=token,
            path=output_path,
            filename=filename,
            expires_at=datetime.now(UTC) + timedelta(seconds=self.settings.file_ttl_seconds),
        )
        self._artifacts[token] = artifact
        return artifact

    def claim(self, token: str) -> DownloadArtifact:
        artifact = self._artifacts.pop(token, None)
        if artifact is None or artifact.expires_at <= datetime.now(UTC) or not artifact.path.is_file():
            if artifact is not None:
                self.delete_workspace(artifact.path.parent)
            raise DownloadNotFoundError()
        return artifact

    def delete_workspace(self, workspace: Path) -> None:
        resolved = workspace.resolve()
        if resolved == self.settings.storage_root or not resolved.is_relative_to(self.settings.storage_root):
            return
        shutil.rmtree(resolved, ignore_errors=True)

    def cleanup_expired(self) -> None:
        now = datetime.now(UTC)
        for token, artifact in list(self._artifacts.items()):
            if artifact.expires_at <= now:
                self._artifacts.pop(token, None)
                self.delete_workspace(artifact.path.parent)

        if not self.settings.storage_root.exists():
            return
        oldest_allowed = time.time() - self.settings.file_ttl_seconds
        for entry in self.settings.storage_root.iterdir():
            if entry.is_dir() and entry.stat().st_mtime < oldest_allowed:
                self.delete_workspace(entry)
