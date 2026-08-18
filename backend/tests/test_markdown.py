import pytest

from app.errors import EmptyContentError
from app.services.markdown import clean_markdown


def test_removes_only_known_edge_wrappers() -> None:
    content = "\ufeff\n好的，我来回答你的问题：\r\n# 标题\r\n希望对你有帮助。\n"
    assert clean_markdown(content) == "# 标题\n"


def test_preserves_matching_phrase_inside_document() -> None:
    content = "# 标题\n\n希望对你有帮助\n\n正文"
    assert "希望对你有帮助" in clean_markdown(content)


def test_rejects_empty_content_after_cleanup() -> None:
    with pytest.raises(EmptyContentError):
        clean_markdown("  \n")
