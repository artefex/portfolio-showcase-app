"""Mock service implementations for testing. No API keys required."""

from langchain_core.messages import AIMessage, BaseMessage


class MockClassifier:
    """Returns a pre-configured classification result."""

    def __init__(self, is_cooking_related: bool = True, reason: str = "mock"):
        self._result = {"is_cooking_related": is_cooking_related, "reason": reason}

    async def classify(self, query: str, history=None) -> dict:
        return self._result


class MockReasoner:
    """Returns a pre-configured AIMessage."""

    def __init__(self, content: str = "", tool_calls: list | None = None):
        self._content = content
        self._tool_calls = tool_calls or []

    async def reason(self, messages: list[BaseMessage], query: str) -> BaseMessage:
        msg = AIMessage(content=self._content)
        if self._tool_calls:
            msg.tool_calls = self._tool_calls
        return msg


class MockCookwareChecker:
    """Returns a pre-configured cookware check result."""

    def __init__(
        self,
        sufficient: bool = True,
        missing: list[str] | None = None,
        suggestions: str = "",
    ):
        self._result = {
            "sufficient": sufficient,
            "missing": missing or [],
            "suggestions": suggestions,
        }

    async def check(self, recipe_text: str, cookware_list: list[str]) -> dict:
        return self._result
