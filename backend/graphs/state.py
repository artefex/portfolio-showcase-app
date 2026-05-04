from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class RecipeGraphState(TypedDict):
    """State that flows through every node in the graph."""

    # Core conversation
    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str

    # Classification
    is_cooking_related: bool

    # Reasoning output
    recipe_detected: bool
    recipe_text: str
    tools_used: list[str]

    # Cookware validation
    cookware_sufficient: bool
    missing_cookware: list[str]
    cookware_suggestions: str

    # Final output
    final_response: str
    debug_log: list[str]
