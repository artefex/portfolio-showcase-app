"""Tests for format_response node."""

from nodes.format_response import format_response_node


def test_format_basic_response(recipe_state):
    """Should assemble final_response from reasoning output."""
    # Simulate reasoning having produced a response in messages
    from langchain_core.messages import AIMessage

    recipe_state["messages"] = [AIMessage(content=recipe_state["recipe_text"])]
    result = format_response_node(recipe_state)
    assert "final_response" in result
    assert len(result["final_response"]) > 0


def test_format_with_cookware_gap(recipe_with_oven_state):
    """When cookware is insufficient, should append cookware note."""
    from langchain_core.messages import AIMessage

    recipe_with_oven_state["messages"] = [
        AIMessage(content=recipe_with_oven_state["recipe_text"])
    ]
    recipe_with_oven_state["cookware_sufficient"] = False
    recipe_with_oven_state["missing_cookware"] = ["oven"]
    recipe_with_oven_state["cookware_suggestions"] = "You can make a stovetop version instead."
    result = format_response_node(recipe_with_oven_state)
    assert "cookware" in result["final_response"].lower() or "oven" in result["final_response"].lower()


def test_format_with_sources(recipe_state):
    """When tools were used, should append sources info."""
    from langchain_core.messages import AIMessage

    recipe_state["messages"] = [AIMessage(content=recipe_state["recipe_text"])]
    recipe_state["tools_used"] = ["tavily_search"]
    result = format_response_node(recipe_state)
    assert "source" in result["final_response"].lower() or "search" in result["final_response"].lower()


def test_format_handles_list_content(recipe_state):
    """When AIMessage.content is a list of content blocks, should extract text."""
    from langchain_core.messages import AIMessage

    recipe_state["messages"] = [AIMessage(content=[
        {"type": "text", "text": "Here is a recipe."},
        {"type": "text", "text": " Enjoy!"},
    ])]
    result = format_response_node(recipe_state)
    assert result["final_response"] == "Here is a recipe. Enjoy!"


def test_format_handles_mixed_content_blocks(recipe_state):
    """When content blocks include non-text types, should skip them gracefully."""
    from langchain_core.messages import AIMessage

    recipe_state["messages"] = [AIMessage(content=[
        {"type": "text", "text": "Recipe here."},
        {"type": "tool_use", "id": "123", "name": "search", "input": {}},
    ])]
    result = format_response_node(recipe_state)
    assert result["final_response"] == "Recipe here."
