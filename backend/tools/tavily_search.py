from config import settings

try:
    from langchain_community.tools.tavily_search import TavilySearchResults

    tavily_tool = TavilySearchResults(
        max_results=3,
        tavily_api_key=settings.tavily_api_key,
    )
except Exception:
    # When TAVILY_API_KEY is not set (e.g. in tests), provide None.
    # The graph won't use it unless the LLM decides to call it.
    tavily_tool = None  # type: ignore[assignment]
