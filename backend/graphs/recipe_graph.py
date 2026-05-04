from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode

from graphs.state import RecipeGraphState
from nodes.classify_query import make_classify_query_node
from nodes.cookware_check import make_cookware_check_node
from nodes.format_response import format_response_node
from nodes.reasoning import make_reasoning_node
from nodes.refuse_query import refuse_query_node
from services.protocols import ClassifierService, CookwareCheckerService, ReasonerService
from tools.tavily_search import tavily_tool


# Routing functions (pure logic, no dependencies)
def route_after_classify(state: RecipeGraphState) -> str:
    return "reasoning" if state["is_cooking_related"] else "refuse_query"


def route_after_reasoning(state: RecipeGraphState) -> str:
    last_message = state["messages"][-1] if state["messages"] else None
    if last_message and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    if state.get("recipe_detected"):
        return "cookware_check"
    return "format_response"


def build_graph(
    classifier: ClassifierService,
    reasoner: ReasonerService,
    cookware_checker: CookwareCheckerService,
):
    """Build and compile the recipe graph with injected services."""
    tool_node = ToolNode([tavily_tool]) if tavily_tool else ToolNode([])

    graph = StateGraph(RecipeGraphState)

    # Add nodes — LLM-dependent nodes use factory functions
    graph.add_node("classify_query", make_classify_query_node(classifier))
    graph.add_node("refuse_query", refuse_query_node)
    graph.add_node("reasoning", make_reasoning_node(reasoner))
    graph.add_node("tools", tool_node)
    graph.add_node("cookware_check", make_cookware_check_node(cookware_checker))
    graph.add_node("format_response", format_response_node)

    graph.set_entry_point("classify_query")
    graph.add_conditional_edges("classify_query", route_after_classify)
    graph.add_edge("refuse_query", END)
    graph.add_conditional_edges("reasoning", route_after_reasoning)
    graph.add_edge("tools", "reasoning")
    graph.add_edge("cookware_check", "format_response")
    graph.add_edge("format_response", END)

    return graph.compile()


# Default production graph — uses real Anthropic services
from services.anthropic import create_default_services  # noqa: E402

_classifier, _reasoner, _cookware_checker = create_default_services()
compiled_graph = build_graph(_classifier, _reasoner, _cookware_checker)
