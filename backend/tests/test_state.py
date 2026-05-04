"""Tests for RecipeGraphState schema."""

import typing

from graphs.state import RecipeGraphState


def test_state_has_all_required_fields():
    """RecipeGraphState must have all fields defined in the blueprint."""
    hints = typing.get_type_hints(RecipeGraphState, include_extras=True)
    required_fields = {
        "messages",
        "user_query",
        "is_cooking_related",
        "recipe_detected",
        "recipe_text",
        "tools_used",
        "cookware_sufficient",
        "missing_cookware",
        "cookware_suggestions",
        "final_response",
        "debug_log",
    }
    assert required_fields.issubset(hints.keys()), (
        f"Missing fields: {required_fields - hints.keys()}"
    )


def test_state_can_be_instantiated(empty_state):
    """An empty state should be constructable with all defaults."""
    assert empty_state["user_query"] == ""
    assert empty_state["is_cooking_related"] is False
    assert empty_state["messages"] == []
    assert empty_state["debug_log"] == []
