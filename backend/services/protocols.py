"""Service protocols following Interface Segregation Principle.

Each LLM-dependent node gets its own narrow interface.
Nodes depend on these protocols, not on concrete LLM implementations.
"""

from typing import Protocol

from langchain_core.messages import BaseMessage


class ClassifierService(Protocol):
    """Classifies whether a user query is cooking-related."""

    async def classify(self, query: str, history: list[BaseMessage] | None = None) -> dict:
        """Return {"is_cooking_related": bool, "reason": str}."""
        ...


class ReasonerService(Protocol):
    """Produces a cooking response, optionally using tools."""

    async def reason(self, messages: list[BaseMessage], query: str) -> BaseMessage:
        """Return an AIMessage with the response (may contain tool_calls)."""
        ...


class CookwareCheckerService(Protocol):
    """Validates a recipe against available cookware."""

    async def check(self, recipe_text: str, cookware_list: list[str]) -> dict:
        """Return {"sufficient": bool, "missing": list[str], "suggestions": str}."""
        ...
