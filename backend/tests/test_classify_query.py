"""Tests for classify_query node — uses MockClassifier (no API keys)."""

import pytest

from nodes.classify_query import make_classify_query_node
from services.mock import MockClassifier


@pytest.mark.asyncio
async def test_classify_cooking_query(cooking_query_state):
    """A cooking-related query should set is_cooking_related=True."""
    node = make_classify_query_node(MockClassifier(is_cooking_related=True, reason="mentions pasta"))
    result = await node(cooking_query_state)
    assert result["is_cooking_related"] is True


@pytest.mark.asyncio
async def test_classify_non_cooking_query(non_cooking_query_state):
    """An off-topic query should set is_cooking_related=False."""
    node = make_classify_query_node(MockClassifier(is_cooking_related=False, reason="sports"))
    result = await node(non_cooking_query_state)
    assert result["is_cooking_related"] is False


@pytest.mark.asyncio
async def test_classify_sets_debug_log(cooking_query_state):
    """Classification should append reasoning to debug_log."""
    node = make_classify_query_node(MockClassifier(is_cooking_related=True, reason="cooking query"))
    result = await node(cooking_query_state)
    assert len(result.get("debug_log", [])) > 0
    assert any("classify" in entry.lower() for entry in result["debug_log"])


@pytest.mark.asyncio
async def test_classify_defaults_to_cooking(cooking_query_state):
    """Default MockClassifier should treat queries as cooking-related."""
    node = make_classify_query_node(MockClassifier())
    result = await node(cooking_query_state)
    assert result["is_cooking_related"] is True
