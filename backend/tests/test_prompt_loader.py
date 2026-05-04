"""Tests for prompt loader utility."""

import pytest

from utils.prompt_loader import load_prompt


def test_load_classify_query_prompt():
    """CLASSIFY_QUERY.txt should load and contain classification instructions."""
    prompt = load_prompt("CLASSIFY_QUERY")
    assert len(prompt) > 50, "Prompt should be a substantive template, not a stub"
    assert "cooking" in prompt.lower()


def test_load_reasoning_prompt():
    """REASONING.txt should load and contain cooking assistant instructions."""
    prompt = load_prompt("REASONING")
    assert len(prompt) > 50
    assert "recipe" in prompt.lower() or "cooking" in prompt.lower()


def test_load_cookware_check_prompt():
    """COOKWARE_CHECK.txt should contain placeholder variables."""
    prompt = load_prompt("COOKWARE_CHECK")
    assert len(prompt) > 50
    assert "{cookware_list}" in prompt
    assert "{recipe_text}" in prompt


def test_load_nonexistent_prompt_raises():
    """Loading a prompt that doesn't exist should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_prompt("NONEXISTENT_PROMPT")
