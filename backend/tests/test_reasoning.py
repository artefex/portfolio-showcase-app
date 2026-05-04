"""Tests for reasoning node — uses MockReasoner (no API keys)."""

import pytest

from nodes.reasoning import make_reasoning_node
from services.mock import MockReasoner

RECIPE_RESPONSE = (
    "## Pasta Carbonara\n\n"
    "**Ingredients:**\n- 400g spaghetti\n- 200g guanciale\n\n"
    "**Instructions:**\n"
    "1. Boil pasta in salted water\n"
    "2. Fry guanciale until crispy\n"
    "3. Mix eggs with pecorino\n"
    "4. Toss everything together\n"
)

NON_RECIPE_RESPONSE = (
    "Chicken should be cooked to an internal temperature of 165°F (74°C) "
    "to ensure it's safe to eat. Use a meat thermometer for accuracy."
)


@pytest.mark.asyncio
async def test_reasoning_returns_response(cooking_query_state):
    """Reasoning node should produce a non-empty response for a cooking query."""
    node = make_reasoning_node(MockReasoner(content=RECIPE_RESPONSE))
    result = await node(cooking_query_state)
    assert "messages" in result
    assert len(result["messages"]) > 0


@pytest.mark.asyncio
async def test_reasoning_detects_recipe(cooking_query_state):
    """A recipe query should set recipe_detected=True."""
    node = make_reasoning_node(MockReasoner(content=RECIPE_RESPONSE))
    result = await node(cooking_query_state)
    assert result.get("recipe_detected") is True
    assert len(result.get("recipe_text", "")) > 0


@pytest.mark.asyncio
async def test_reasoning_non_recipe(empty_state):
    """A general cooking tip question should set recipe_detected=False."""
    state = {
        **empty_state,
        "user_query": "What temperature should I cook chicken to?",
        "is_cooking_related": True,
    }
    node = make_reasoning_node(MockReasoner(content=NON_RECIPE_RESPONSE))
    result = await node(state)
    assert result.get("recipe_detected") is False
    assert result.get("recipe_text") == ""


@pytest.mark.asyncio
async def test_reasoning_detects_recipe_from_list_content(cooking_query_state):
    """Recipe detection should work when AIMessage.content is a list of blocks."""
    from langchain_core.messages import AIMessage

    class ListContentReasoner:
        async def reason(self, messages, query):
            return AIMessage(content=[
                {"type": "text", "text": "## Pasta\n\n1. Boil water\n2. Cook pasta"},
            ])

    node = make_reasoning_node(ListContentReasoner())
    result = await node(cooking_query_state)
    assert result.get("recipe_detected") is True
    assert "Pasta" in result.get("recipe_text", "")
