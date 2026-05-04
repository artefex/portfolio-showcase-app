import logging
from collections.abc import Callable

from graphs.state import RecipeGraphState
from services.protocols import CookwareCheckerService
from tools.cookware import AVAILABLE_COOKWARE

logger = logging.getLogger("recipe_chatbot")


def make_cookware_check_node(checker: CookwareCheckerService) -> Callable:
    """Factory: returns a LangGraph node that uses the given CookwareCheckerService."""

    async def cookware_check_node(state: RecipeGraphState) -> dict:
        """Validate recipe against available cookware."""
        logger.info(
            "cookware_check: evaluating recipe_text length=%d against %d items",
            len(state.get("recipe_text", "")), len(AVAILABLE_COOKWARE),
        )

        result = await checker.check(state["recipe_text"], AVAILABLE_COOKWARE)
        sufficient = result["sufficient"]
        missing = result["missing"]
        suggestions = result["suggestions"]

        logger.info(
            "cookware_check: sufficient=%s, missing=%s", sufficient, missing,
        )

        return {
            "cookware_sufficient": sufficient,
            "missing_cookware": missing,
            "cookware_suggestions": suggestions,
            "debug_log": [f"cookware_check: sufficient={sufficient}, missing={missing}"],
        }

    return cookware_check_node
