"""
Agent Graph — LangGraph state machine for refund-not-received workflow.

Flow:
  START
    → classify_intent
    → [route_by_intent]
      ├─ unclear       → ask_clarification → END
      ├─ other         → ask_clarification → END
      └─ refund_inquiry
           → [check_order_id]
             ├─ missing (retries < MAX) → ask_order_id → END (wait for reply)
             ├─ missing (retries >= MAX) → escalate → END
             └─ present
                  → query_refund_status
                  → [need_account_lookup?]
                    ├─ yes (status=failed) → query_account_info → route_result
                    └─ no                 → route_result
                  → [route_result]
                    ├─ direct_reply → generate_response → END
                    ├─ escalate     → build_escalation  → END
                    └─ error        → order_not_found   → END
"""

from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes.intent import classify_intent
from agent.nodes.collector import check_order_id, increment_retry, MAX_RETRIES
from agent.nodes.tools_node import run_refund_status, run_account_info
from agent.nodes.router import route_result
from agent.nodes.responder import (
    generate_response,
    generate_ask_order_id,
    generate_ask_clarification,
    generate_order_not_found,
)
from agent.nodes.escalator import build_escalation


# ── Edge conditions ───────────────────────────────────────────────────────────

def _route_by_intent(state: AgentState) -> str:
    intent = state.get("intent", "other")
    if intent == "refund_status_inquiry":
        return "check_order_id"
    return "ask_clarification"


def _route_by_order_id(state: AgentState) -> str:
    order_id = state.get("order_id")
    retries = state.get("collect_retries", 0)

    if order_id:
        return "query_refund_status"
    if retries >= MAX_RETRIES:
        return "escalate"
    return "ask_order_id"


def _route_after_refund_status(state: AgentState) -> str:
    refund_status = state.get("refund_status")
    failure_reason = state.get("failure_reason_code")

    # API errors → route to router which will escalate
    if failure_reason and (
        failure_reason == "order_not_found"
        or failure_reason.startswith("api_timeout")
    ):
        return "route_result"

    # Failed → need account info
    if refund_status == "failed":
        return "query_account_info"

    return "route_result"


def _route_by_action(state: AgentState) -> str:
    action = state.get("next_action", "escalate")
    if action == "direct_reply":
        return "generate_response"
    if action == "error":
        return "order_not_found"
    return "escalate"


# ── Build graph ───────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    g = StateGraph(AgentState)

    # Register nodes
    g.add_node("classify_intent", classify_intent)
    g.add_node("check_order_id", check_order_id)
    g.add_node("increment_retry", increment_retry)
    g.add_node("ask_order_id", generate_ask_order_id)
    g.add_node("ask_clarification", generate_ask_clarification)
    g.add_node("query_refund_status", run_refund_status)
    g.add_node("query_account_info", run_account_info)
    g.add_node("route_result", route_result)
    g.add_node("generate_response", generate_response)
    g.add_node("order_not_found", generate_order_not_found)
    g.add_node("escalate", build_escalation)

    # Entry
    g.set_entry_point("classify_intent")

    # Edges
    g.add_conditional_edges(
        "classify_intent",
        _route_by_intent,
        {"check_order_id": "check_order_id", "ask_clarification": "ask_clarification"},
    )

    g.add_conditional_edges(
        "check_order_id",
        _route_by_order_id,
        {
            "query_refund_status": "query_refund_status",
            "ask_order_id": "increment_retry",
            "escalate": "escalate",
        },
    )

    g.add_edge("increment_retry", "ask_order_id")

    g.add_conditional_edges(
        "query_refund_status",
        _route_after_refund_status,
        {
            "query_account_info": "query_account_info",
            "route_result": "route_result",
        },
    )

    g.add_edge("query_account_info", "route_result")

    g.add_conditional_edges(
        "route_result",
        _route_by_action,
        {
            "generate_response": "generate_response",
            "order_not_found": "order_not_found",
            "escalate": "escalate",
        },
    )

    # Terminal nodes
    for node in ("ask_order_id", "ask_clarification", "generate_response",
                 "order_not_found", "escalate"):
        g.add_edge(node, END)

    return g.compile()


# Singleton — import and use directly
agent = build_graph()
