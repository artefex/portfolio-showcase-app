"""Integration tests for the full recipe graph — uses mock services (no API keys)."""

import pytest

from graphs.recipe_graph import build_graph
from services.mock import MockClassifier, MockCookwareChecker, MockReasoner

RECIPE_RESPONSE = (
    "## Pasta Carbonara\n\n"
    "1. Boil pasta\n2. Fry guanciale\n3. Mix eggs\n4. Combine"
)
NON_RECIPE_RESPONSE = "Cook chicken to 165°F (74°C) for safety."
BAKING_RECIPE = (
    "## Chocolate Cake\n\n"
    "1. Preheat oven to 350°F\n2. Mix ingredients\n3. Bake for 30 min"
)

INITIAL_STATE = {
    "messages": [],
    "user_query": "",
    "is_cooking_related": False,
    "recipe_detected": False,
    "recipe_text": "",
    "tools_used": [],
    "cookware_sufficient": True,
    "missing_cookware": [],
    "cookware_suggestions": "",
    "final_response": "",
    "debug_log": [],
}


@pytest.mark.asyncio
async def test_full_graph_cooking_query():
    """A cooking query should flow through the graph and produce a final_response."""
    graph = build_graph(
        classifier=MockClassifier(is_cooking_related=True),
        reasoner=MockReasoner(content=RECIPE_RESPONSE),
        cookware_checker=MockCookwareChecker(sufficient=True),
    )
    result = await graph.ainvoke({
        **INITIAL_STATE,
        "user_query": "How do I make pasta carbonara?",
    })
    assert result["is_cooking_related"] is True
    assert len(result["final_response"]) > 0


@pytest.mark.asyncio
async def test_full_graph_refusal():
    """An off-topic query should produce a refusal response."""
    graph = build_graph(
        classifier=MockClassifier(is_cooking_related=False),
        reasoner=MockReasoner(),
        cookware_checker=MockCookwareChecker(),
    )
    result = await graph.ainvoke({
        **INITIAL_STATE,
        "user_query": "Who won the Super Bowl?",
    })
    assert result["is_cooking_related"] is False
    assert "cooking" in result["final_response"].lower()


@pytest.mark.asyncio
async def test_full_graph_cookware_check_runs_for_recipe():
    """A recipe query with missing cookware should be flagged."""
    graph = build_graph(
        classifier=MockClassifier(is_cooking_related=True),
        reasoner=MockReasoner(content=BAKING_RECIPE),
        cookware_checker=MockCookwareChecker(
            sufficient=False,
            missing=["oven"],
            suggestions="Use a stovetop version.",
        ),
    )
    result = await graph.ainvoke({
        **INITIAL_STATE,
        "user_query": "How do I bake a chocolate cake?",
    })
    assert result["is_cooking_related"] is True
    assert result["recipe_detected"] is True
    assert result["cookware_sufficient"] is False
    assert "oven" in [m.lower() for m in result["missing_cookware"]]


@pytest.mark.asyncio
async def test_full_graph_cookware_check_skips_for_non_recipe():
    """A general cooking tip should skip the cookware check."""
    graph = build_graph(
        classifier=MockClassifier(is_cooking_related=True),
        reasoner=MockReasoner(content=NON_RECIPE_RESPONSE),
        cookware_checker=MockCookwareChecker(),
    )
    result = await graph.ainvoke({
        **INITIAL_STATE,
        "user_query": "What temperature should I cook chicken to?",
    })
    assert result["is_cooking_related"] is True
    assert result["cookware_sufficient"] is True
    assert result["missing_cookware"] == []
