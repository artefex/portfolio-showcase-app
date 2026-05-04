import logging

from graphs.state import RecipeGraphState
from utils.content import extract_text

logger = logging.getLogger("recipe_chatbot")


def format_response_node(state: RecipeGraphState) -> dict:
    """Assemble final_response from available state. Deterministic — no LLM call."""
    # Start with the last AI message content
    parts = []

    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        content = extract_text(last_msg.content) if hasattr(last_msg, "content") else str(last_msg)
        parts.append(content)

    # Append cookware warning if items are missing
    if not state.get("cookware_sufficient", True) and state.get("missing_cookware"):
        missing = ", ".join(state["missing_cookware"])
        parts.append(
            f"\n\n---\n\n"
            f"⚠️ **Cookware Alert:** You don't have: **{missing}**.\n\n"
            f"Your available equipment: Spatula, Frying Pan, Little Pot, "
            f"Stovetop, Whisk, Knife, Ladle, Spoon."
        )
        if state.get("cookware_suggestions"):
            parts.append(f"\n**Suggested adaptation:** {state['cookware_suggestions']}")

    # Append sources if tools were used
    if state.get("tools_used"):
        tools = ", ".join(state["tools_used"])
        parts.append(f"\n\n📎 *Sources: Results from {tools}*")

    final_response = "\n".join(parts) if parts else "I wasn't able to generate a response."

    logger.info(
        "format_response: cookware_sufficient=%s, missing=%s, response_length=%d",
        state.get("cookware_sufficient", True),
        state.get("missing_cookware", []),
        len(final_response),
    )

    return {"final_response": final_response}
