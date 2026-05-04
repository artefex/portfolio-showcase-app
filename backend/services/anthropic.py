"""Concrete service implementations backed by ChatAnthropic."""

import json

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from config import settings
from tools.tavily_search import tavily_tool
from utils.prompt_loader import load_prompt


class AnthropicClassifier:
    """Classifies queries using a lightweight Claude call."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self._llm = ChatAnthropic(
            model=model, api_key=api_key, max_tokens=256, temperature=0,
        )

    async def classify(self, query: str, history: list[BaseMessage] | None = None) -> dict:
        system_prompt = load_prompt("CLASSIFY_QUERY")
        messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]
        if history:
            messages.extend(history)
        messages.append(HumanMessage(content=query))
        response = await self._llm.ainvoke(messages)
        try:
            parsed = json.loads(response.content)
            return {
                "is_cooking_related": parsed.get("is_cooking_related", False),
                "reason": parsed.get("reason", ""),
            }
        except (json.JSONDecodeError, AttributeError):
            return {
                "is_cooking_related": True,
                "reason": "Classification parsing failed — defaulting to cooking-related",
            }


class AnthropicReasoner:
    """Main reasoning with optional tool binding."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        llm = ChatAnthropic(
            model=model, api_key=api_key, max_tokens=4096, temperature=0.3,
        )
        tools = [tavily_tool] if tavily_tool else []
        self._llm = llm.bind_tools(tools) if tools else llm

    async def reason(self, messages: list[BaseMessage], query: str) -> BaseMessage:
        from tools.cookware import AVAILABLE_COOKWARE

        prompt_template = load_prompt("REASONING")
        formatted_list = ", ".join(AVAILABLE_COOKWARE)
        system_prompt = prompt_template.format(cookware_list=formatted_list)
        full_messages = [
            SystemMessage(content=system_prompt),
            *messages,
            HumanMessage(content=query),
        ]
        return await self._llm.ainvoke(full_messages)


class AnthropicCookwareChecker:
    """Validates cookware requirements using an LLM."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self._llm = ChatAnthropic(
            model=model, api_key=api_key, max_tokens=1024, temperature=0,
        )

    async def check(self, recipe_text: str, cookware_list: list[str]) -> dict:
        prompt_template = load_prompt("COOKWARE_CHECK")
        formatted_list = "\n".join(f"- {item}" for item in cookware_list)
        prompt = prompt_template.format(
            cookware_list=formatted_list,
            recipe_text=recipe_text,
        )
        response = await self._llm.ainvoke([
            SystemMessage(content=prompt),
            HumanMessage(content="Evaluate the cookware requirements for this recipe."),
        ])
        try:
            parsed = json.loads(response.content)
            return {
                "sufficient": parsed.get("sufficient", True),
                "missing": parsed.get("missing", []),
                "suggestions": parsed.get("suggestions", ""),
            }
        except (json.JSONDecodeError, AttributeError):
            return {"sufficient": False, "missing": ["unknown"], "suggestions": "Could not verify cookware requirements — please review the recipe manually."}


def create_default_services() -> tuple[AnthropicClassifier, AnthropicReasoner, AnthropicCookwareChecker]:
    """Factory that creates production services from settings."""
    api_key = settings.anthropic_api_key
    return (
        AnthropicClassifier(api_key=api_key),
        AnthropicReasoner(api_key=api_key),
        AnthropicCookwareChecker(api_key=api_key),
    )
