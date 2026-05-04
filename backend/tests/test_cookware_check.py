"""Tests for cookware_check node — uses MockCookwareChecker (no API keys)."""

import pytest

from nodes.cookware_check import make_cookware_check_node
from services.mock import MockCookwareChecker


@pytest.mark.asyncio
async def test_cookware_sufficient(recipe_state):
    """Pasta carbonara with frying pan + large pot should be sufficient."""
    node = make_cookware_check_node(MockCookwareChecker(sufficient=True))
    result = await node(recipe_state)
    assert result["cookware_sufficient"] is True
    assert result["missing_cookware"] == []


@pytest.mark.asyncio
async def test_cookware_insufficient(recipe_with_oven_state):
    """A baking recipe should flag missing oven."""
    node = make_cookware_check_node(MockCookwareChecker(
        sufficient=False,
        missing=["oven"],
        suggestions="Use a stovetop version.",
    ))
    result = await node(recipe_with_oven_state)
    assert result["cookware_sufficient"] is False
    assert len(result["missing_cookware"]) > 0
    missing_lower = [item.lower() for item in result["missing_cookware"]]
    assert any("oven" in item for item in missing_lower)


@pytest.mark.asyncio
async def test_cookware_suggestions_when_insufficient(recipe_with_oven_state):
    """When cookware is insufficient, should provide alternative suggestions."""
    node = make_cookware_check_node(MockCookwareChecker(
        sufficient=False,
        missing=["oven"],
        suggestions="You can make a stovetop version using a frying pan instead.",
    ))
    result = await node(recipe_with_oven_state)
    assert result["cookware_sufficient"] is False
    assert len(result.get("cookware_suggestions", "")) > 0


@pytest.mark.asyncio
async def test_cookware_defaults_to_sufficient(recipe_state):
    """Default MockCookwareChecker should report sufficient."""
    node = make_cookware_check_node(MockCookwareChecker())
    result = await node(recipe_state)
    assert result["cookware_sufficient"] is True
