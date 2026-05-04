"""Tests for utils.content.extract_text — content block coercion."""

from utils.content import extract_text


def test_extract_text_from_string():
    """Plain string content should pass through unchanged."""
    assert extract_text("Hello world") == "Hello world"


def test_extract_text_from_list_of_text_blocks():
    """List of text content blocks should be concatenated."""
    content = [
        {"type": "text", "text": "Hello "},
        {"type": "text", "text": "world!"},
    ]
    assert extract_text(content) == "Hello world!"


def test_extract_text_skips_non_text_blocks():
    """Non-text blocks (e.g., tool_use) should contribute empty string."""
    content = [
        {"type": "text", "text": "Recipe here."},
        {"type": "tool_use", "id": "123", "name": "search", "input": {}},
    ]
    assert extract_text(content) == "Recipe here."


def test_extract_text_empty_list():
    """Empty list should produce empty string."""
    assert extract_text([]) == ""


def test_extract_text_fallback_to_str():
    """Non-string, non-list content should be coerced via str()."""
    assert extract_text(42) == "42"
