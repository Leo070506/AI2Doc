"""Conservative Markdown normalization for the MVP."""

from __future__ import annotations

import re

from app.errors import EmptyContentError

OPENING_WRAPPERS = frozenset(
    {
        "好的，我来回答你的问题",
        "好的，下面是我的回答",
        "当然可以，以下是我的回答",
        "sure, here's the answer",
    }
)
CLOSING_WRAPPERS = frozenset(
    {
        "希望对你有帮助",
        "希望以上内容对你有帮助",
        "hope this helps",
    }
)


def _comparable(line: str) -> str:
    return re.sub(r"[。！!：:]$", "", line.strip()).casefold()


def clean_markdown(content: str) -> str:
    """Normalize line endings and remove exact wrapper lines at document edges."""

    normalized = content.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.split("\n")

    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()

    if lines and _comparable(lines[0]) in OPENING_WRAPPERS:
        lines.pop(0)
    if lines and _comparable(lines[-1]) in CLOSING_WRAPPERS:
        lines.pop()

    cleaned = "\n".join(lines).strip()
    if not cleaned:
        raise EmptyContentError()
    return f"{cleaned}\n"
