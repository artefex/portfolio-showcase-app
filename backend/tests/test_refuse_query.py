"""Tests for refuse_query node."""

from nodes.refuse_query import refuse_query_node


def test_refuse_sets_final_response(non_cooking_query_state):
    """Refuse node should set a polite refusal in final_response."""
    result = refuse_query_node(non_cooking_query_state)
    assert "final_response" in result
    assert len(result["final_response"]) > 0
    assert "cooking" in result["final_response"].lower()


def test_refuse_is_deterministic(non_cooking_query_state):
    """Refuse node should return the same response every time (no LLM)."""
    result1 = refuse_query_node(non_cooking_query_state)
    result2 = refuse_query_node(non_cooking_query_state)
    assert result1["final_response"] == result2["final_response"]
