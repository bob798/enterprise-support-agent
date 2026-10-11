"""
Node: Response Generator

Fills response templates from tool output.
Every factual field traces to state (which came from tool output).
No LLM inference on financial values.
"""

from agent.state import AgentState
from agent.prompts.response import render


def generate_response(state: AgentState) -> dict:
    refund_status = state.get("refund_status")
    failure_reason = state.get("failure_reason_code")
    order_id = state.get("order_id", "")
    amount = state.get("refund_amount", "")
    currency = state.get("refund_currency", "")
    expected_arrival = state.get("expected_arrival", "3–5 个工作日")

    common = dict(
        order_id=order_id,
        amount=amount,
        currency=currency,
        expected_arrival=expected_arrival,
    )

    if refund_status == "pending":
        text = render("pending", **common)
    elif refund_status == "initiated":
        text = render("initiated", **common)
    elif refund_status == "succeeded":
        text = render("succeeded", **common)
    elif refund_status == "failed":
        key = failure_reason if failure_reason in (
            "insufficient_funds", "account_frozen", "risk_control"
        ) else "error"
        text = render(key, **common)
    else:
        text = render("error")

    return {
        "response_text": text,
        "messages": [{"role": "assistant", "content": text}],
    }


def generate_ask_order_id(state: AgentState) -> dict:
    text = render("ask_order_id")
    return {
        "response_text": text,
        "messages": [{"role": "assistant", "content": text}],
    }


def generate_ask_clarification(state: AgentState) -> dict:
    text = render("ask_clarification")
    return {
        "response_text": text,
        "messages": [{"role": "assistant", "content": text}],
    }


def generate_order_not_found(state: AgentState) -> dict:
    order_id = state.get("order_id", "")
    text = render("order_not_found", order_id=order_id)
    return {
        "response_text": text,
        "messages": [{"role": "assistant", "content": text}],
    }
