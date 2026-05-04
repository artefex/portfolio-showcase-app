import json

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from langchain_core.messages import AIMessage, HumanMessage

from graphs.recipe_graph import compiled_graph
from schemas.api import ChatRequest
from utils.content import extract_text
from utils.logging import setup_logging

logger = setup_logging()

app = FastAPI(title="Recipe Assistant Showcase API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def sse_event(event: str, data: dict) -> str:
    """Format an SSE event."""
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(request: ChatRequest, debug: bool = Query(False)):
    """SSE streaming chat endpoint."""

    async def event_stream():
        try:
            # Convert history to LangChain messages
            history_messages = []
            for msg in request.history:
                if msg.role == "user":
                    history_messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    history_messages.append(AIMessage(content=msg.content))

            initial_state = {
                "messages": history_messages,
                "user_query": request.message,
                "is_cooking_related": False,
                "recipe_detected": False,
                "recipe_text": "",
                "tools_used": [],
                "cookware_sufficient": True,
                "missing_cookware": [],
                "cookware_suggestions": "",
                "final_response": "",
                "debug_log": [],
            }

            current_node = ""
            final_state = None

            async for event in compiled_graph.astream_events(
                initial_state, version="v2"
            ):
                event_type = event.get("event", "")
                event_name = event.get("name", "")

                # Node start/end events
                if event_type == "on_chain_start" and event_name in (
                    "classify_query",
                    "refuse_query",
                    "reasoning",
                    "cookware_check",
                    "format_response",
                    "tools",
                ):
                    current_node = event_name
                    yield sse_event("node", {"node": event_name, "status": "started"})

                    if debug:
                        yield sse_event("debug", {
                            "node": event_name,
                            "reasoning": f"Entering {event_name} node",
                        })

                elif event_type == "on_chain_end" and event_name in (
                    "classify_query",
                    "refuse_query",
                    "reasoning",
                    "cookware_check",
                    "format_response",
                    "tools",
                ):
                    output = event.get("data", {}).get("output", {})
                    yield sse_event("node", {
                        "node": event_name,
                        "status": "completed",
                    })

                    # Capture tool events
                    if event_name == "tools" and isinstance(output, dict):
                        yield sse_event("tool", {
                            "tool": "tavily_search",
                            "status": "result",
                        })

                    # Capture cookware results
                    if event_name == "cookware_check" and isinstance(output, dict):
                        yield sse_event("cookware", {
                            "sufficient": output.get("cookware_sufficient", True),
                            "missing": output.get("missing_cookware", []),
                            "suggestions": output.get("cookware_suggestions", ""),
                        })

                # Stream tokens only from the reasoning node's LLM call
                elif event_type == "on_chat_model_stream":
                    source_node = event.get("metadata", {}).get("langgraph_node", current_node)
                    if source_node == "reasoning":
                        chunk = event.get("data", {}).get("chunk")
                        if chunk and hasattr(chunk, "content") and chunk.content:
                            yield sse_event("token", {"content": extract_text(chunk.content)})

                # Capture final graph output
                elif event_type == "on_chain_end" and event_name == "LangGraph":
                    final_state = event.get("data", {}).get("output", {})

            # Send final done event
            if final_state:
                cookware_check = None
                if not final_state.get("cookware_sufficient", True):
                    cookware_check = {
                        "sufficient": False,
                        "missing": final_state.get("missing_cookware", []),
                        "suggestions": final_state.get("cookware_suggestions", ""),
                    }

                yield sse_event("done", {
                    "final_response": final_state.get("final_response", ""),
                    "tools_used": final_state.get("tools_used", []),
                    "cookware_check": cookware_check,
                })

                if debug and final_state.get("debug_log"):
                    for entry in final_state["debug_log"]:
                        yield sse_event("debug", {"node": "summary", "reasoning": entry})
            else:
                yield sse_event("done", {
                    "final_response": "No response generated.",
                    "tools_used": [],
                    "cookware_check": None,
                })

        except Exception as e:
            yield sse_event("error", {"message": str(e), "code": "INTERNAL_ERROR"})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
