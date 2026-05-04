import logging

from graphs.state import RecipeGraphState

logger = logging.getLogger("recipe_chatbot")

REFUSAL_MESSAGE = (
    "I'm a cooking assistant and can only help with food-related questions. "
    "Feel free to ask me about recipes, cooking techniques, or ingredients!"
)


def refuse_query_node(state: RecipeGraphState) -> dict:
    """Terminal node — returns a polite refusal for non-cooking queries."""
    logger.info("refuse_query: returning refusal for query=%s", state.get("user_query", ""))
    return {"final_response": REFUSAL_MESSAGE}
