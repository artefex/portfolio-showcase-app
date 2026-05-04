import logging
from collections.abc import Callable

from graphs.state import RecipeGraphState
from services.protocols import ClassifierService

logger = logging.getLogger("recipe_chatbot")


def make_classify_query_node(classifier: ClassifierService) -> Callable:
    """Factory: returns a LangGraph node that uses the given ClassifierService."""

    async def classify_query_node(state: RecipeGraphState) -> dict:
        """Classify whether the user's query is cooking-related."""
        result = await classifier.classify(state["user_query"], state.get("messages"))
        is_cooking = result["is_cooking_related"]
        reason = result.get("reason", "")

        logger.info("classify_query: is_cooking_related=%s, reason=%s", is_cooking, reason)

        debug_entry = f"classify_query: is_cooking_related={is_cooking}, reason={reason}"
        return {
            "is_cooking_related": is_cooking,
            "debug_log": [debug_entry],
        }

    return classify_query_node
