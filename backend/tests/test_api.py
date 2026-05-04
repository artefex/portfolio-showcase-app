"""Tests for FastAPI endpoints — graph boundary mock (no API keys)."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


def _make_mock_graph(final_response: str = "Test response."):
    """Create a mock compiled graph that yields a single on_chain_end event."""
    mock = AsyncMock()

    async def mock_astream_events(*args, **kwargs):
        yield {"event": "on_chain_end", "data": {"output": {
            "final_response": final_response,
            "is_cooking_related": True,
            "tools_used": [],
            "cookware_sufficient": True,
            "missing_cookware": [],
            "cookware_suggestions": "",
        }}}

    mock.astream_events = mock_astream_events
    return mock


@pytest.mark.asyncio
async def test_health_endpoint():
    """GET /health should return 200 with status ok."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_chat_endpoint_returns_sse():
    """POST /api/chat should return content-type text/event-stream."""
    with patch("main.compiled_graph", _make_mock_graph("Here is a recipe.")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/chat",
                json={"message": "How do I make pasta?"},
            )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_chat_endpoint_sends_done_event():
    """Response should contain an event: done line."""
    with patch("main.compiled_graph", _make_mock_graph()):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/chat",
                json={"message": "How do I make pasta?"},
            )
    assert "event: done" in response.text


@pytest.mark.asyncio
async def test_chat_endpoint_validates_input():
    """Empty message should return 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/chat",
            json={"message": ""},
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_endpoint_error_on_missing_message():
    """Missing message field should return 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/chat", json={})
    assert response.status_code == 422


def _make_mock_graph_with_list_content():
    """Create a mock graph where chunk.content is a list of content blocks."""
    mock = AsyncMock()

    async def mock_astream_events(*args, **kwargs):
        # Simulate on_chat_model_stream with list content and langgraph metadata
        yield {
            "event": "on_chat_model_stream",
            "name": "ChatAnthropic",
            "metadata": {"langgraph_node": "reasoning"},
            "data": {"chunk": type("Chunk", (), {"content": [
                {"type": "text", "text": "Hello "},
                {"type": "text", "text": "world!"},
            ]})()},
        }
        # Then emit final graph output
        yield {"event": "on_chain_end", "name": "LangGraph", "data": {"output": {
            "final_response": "Hello world!",
            "is_cooking_related": True,
            "tools_used": [],
            "cookware_sufficient": True,
            "missing_cookware": [],
            "cookware_suggestions": "",
        }}}

    mock.astream_events = mock_astream_events
    return mock


@pytest.mark.asyncio
async def test_chat_endpoint_handles_list_content():
    """SSE tokens should be plain strings even when chunk.content is a list."""
    with patch("main.compiled_graph", _make_mock_graph_with_list_content()):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/chat",
                json={"message": "How do I make pasta?"},
            )
    assert response.status_code == 200
    # Token data should contain a plain string, not [object Object]
    assert '"content": "Hello world!"' in response.text
    assert "[object Object]" not in response.text


def _make_mock_graph_with_classify_tokens():
    """Mock graph that emits tokens from both classify and reasoning nodes (via metadata)."""
    mock = AsyncMock()

    async def mock_astream_events(*args, **kwargs):
        # Classify node emits LLM tokens (these should NOT be streamed)
        yield {
            "event": "on_chat_model_stream",
            "name": "ChatAnthropic",
            "metadata": {"langgraph_node": "classify_query"},
            "data": {"chunk": type("Chunk", (), {
                "content": '{"is_cooking_related": true}',
            })()},
        }
        # Reasoning node emits tokens (these SHOULD be streamed)
        yield {
            "event": "on_chat_model_stream",
            "name": "ChatAnthropic",
            "metadata": {"langgraph_node": "reasoning"},
            "data": {"chunk": type("Chunk", (), {"content": "Here is a recipe."})()},
        }
        # Cookware check node emits LLM tokens (these should NOT be streamed)
        yield {
            "event": "on_chat_model_stream",
            "name": "ChatAnthropic",
            "metadata": {"langgraph_node": "cookware_check"},
            "data": {"chunk": type("Chunk", (), {
                "content": '{"sufficient": true}',
            })()},
        }
        # Final graph output
        yield {"event": "on_chain_end", "name": "LangGraph", "data": {"output": {
            "final_response": "Here is a recipe.",
            "is_cooking_related": True,
            "tools_used": [],
            "cookware_sufficient": True,
            "missing_cookware": [],
            "cookware_suggestions": "",
        }}}

    mock.astream_events = mock_astream_events
    return mock


@pytest.mark.asyncio
async def test_chat_endpoint_filters_non_reasoning_tokens():
    """Only tokens from the reasoning node should be streamed; classify/cookware tokens filtered."""
    with patch("main.compiled_graph", _make_mock_graph_with_classify_tokens()):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/chat",
                json={"message": "How do I make pasta?"},
            )
    assert response.status_code == 200
    # Only reasoning tokens should appear in token events
    assert '"content": "Here is a recipe."' in response.text
    # Classification and cookware JSON must NOT appear in token events
    token_section = response.text.split("event: done")[0]
    assert "is_cooking_related" not in token_section
    assert '"sufficient"' not in token_section
