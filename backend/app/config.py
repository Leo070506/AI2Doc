"""Environment-backed application settings."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = BACKEND_DIR.parent


def _cors_origins() -> tuple[str, ...]:
    raw = os.getenv("AI2DOC_CORS_ORIGINS", "http://localhost:5173")
    return tuple(origin.strip() for origin in raw.split(",") if origin.strip())


@dataclass(frozen=True, slots=True)
class Settings:
    pandoc_path: str = field(default_factory=lambda: os.getenv("AI2DOC_PANDOC_PATH", "pandoc"))
    templates_root: Path = field(
        default_factory=lambda: Path(
            os.getenv("AI2DOC_TEMPLATES_ROOT", str(PROJECT_DIR / "templates"))
        ).resolve()
    )
    storage_root: Path = field(
        default_factory=lambda: Path(
            os.getenv("AI2DOC_STORAGE_ROOT", str(BACKEND_DIR / "app" / "storage" / "temp"))
        ).resolve()
    )
    max_input_bytes: int = field(
        default_factory=lambda: int(os.getenv("AI2DOC_MAX_INPUT_BYTES", str(1024 * 1024)))
    )
    max_output_bytes: int = field(
        default_factory=lambda: int(os.getenv("AI2DOC_MAX_OUTPUT_BYTES", str(10 * 1024 * 1024)))
    )
    conversion_timeout_seconds: int = field(
        default_factory=lambda: int(os.getenv("AI2DOC_CONVERSION_TIMEOUT_SECONDS", "30"))
    )
    file_ttl_seconds: int = field(
        default_factory=lambda: int(os.getenv("AI2DOC_FILE_TTL_SECONDS", "3600"))
    )
    cleanup_interval_seconds: int = field(
        default_factory=lambda: int(os.getenv("AI2DOC_CLEANUP_INTERVAL_SECONDS", "60"))
    )
    cors_origins: tuple[str, ...] = field(default_factory=_cors_origins)


@lru_cache
def get_settings() -> Settings:
    return Settings()
