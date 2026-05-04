"""Utility for coercing LangChain message content to plain text."""


def extract_text(content) -> str:
    """Coerce LangChain message content to a plain string.

    LangChain AIMessage.content can be either a str or a list of content blocks
    (e.g., [{"type": "text", "text": "..."}, {"type": "tool_use", ...}]).
    This function normalises both forms to a plain string.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return str(content)
