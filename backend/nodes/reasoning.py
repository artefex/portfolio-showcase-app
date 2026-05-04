import logging
from collections.abc import Callable

from graphs.state import RecipeGraphState
from services.protocols import ReasonerService
from utils.content import extract_text

logger = logging.getLogger("recipe_chatbot")


def make_reasoning_node(reasoner: ReasonerService) -> Callable:
    """Factory: returns a LangGraph node that uses the given ReasonerService."""

    async def reasoning_node(state: RecipeGraphState) -> dict:
        """Main LLM reasoning node. Produces a cooking response, optionally using tools."""
        response = await reasoner.reason(state["messages"], state["user_query"])

        # Extract text from content (handles both str and list content blocks)
        content = extract_text(response.content) if hasattr(response, "content") else ""

        # Check if the response contains a recipe (heuristic)
        content_lower = content.lower()
        recipe_indicators = [
            "1.", "step 1", "instructions:", "ingredients:",
            "2.", "step 2", "recipe", "preparation:",
            "cook for", "minutes", "tablespoon", "teaspoon",
        ]
        recipe_detected = any(indicator in content_lower for indicator in recipe_indicators)

        # Track tool usage
        tools_used = list(state.get("tools_used", []))

        logger.info(
            "reasoning: recipe_detected=%s, content_length=%d, tools_used=%s",
            recipe_detected, len(content), tools_used,
        )

        return {
            "messages": [response],
            "recipe_detected": recipe_detected,
            "recipe_text": content if recipe_detected else "",
            "tools_used": tools_used,
            "debug_log": [f"reasoning: recipe_detected={recipe_detected}"],
        }

    return reasoning_node
