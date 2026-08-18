"""Whitelisted DOCX reference templates."""

from pathlib import Path

from app.config import Settings
from app.errors import ConversionFailedError, InvalidTemplateError

TEMPLATE_NAMES = frozenset({"academic", "report", "notes"})


def resolve_template(settings: Settings, template_name: str) -> Path:
    if template_name not in TEMPLATE_NAMES:
        raise InvalidTemplateError()

    template_path = (settings.templates_root / template_name / "template.docx").resolve()
    if not template_path.is_relative_to(settings.templates_root):
        raise InvalidTemplateError()
    if not template_path.is_file():
        raise ConversionFailedError()
    return template_path
