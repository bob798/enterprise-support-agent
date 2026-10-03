"""
Node: Escalation Builder

Assembles structured handoff payload for human agent.
All 6 required fields must be present — validated before sending.
"""

from datetime import datetime, timezone
from agent.state import AgentState
from agent.prompts.response import render

REQUIRED_FIELDS = [
    "order_id",
    "refund_status",
    "failure_reason_code",
    "merchant_original_message",
    "agent_reasoning",
    "recommended_next_step",
]

_REASONING_TEMPLATES = {
    "bank_error": (
        "Queried order {order_id}: status=failed, failure_reason=bank_error. "
        "Account status={account_status}, balance sufficient. "
        "Root cause requires bank/channel investigation — outside agent scope."
    ),
    "order_expired": (
        "Queried order {order_id}: status=failed, failure_reason=order_expired. "
        "Refund eligibility window may have passed. Policy review required."
    ),
    "order_not_found": (
        "Order ID {order_id} was not found in the Order/Transaction system. "
        "Merchant confirmed this is the correct order number."
    ),
    "unknown": (
        "Queried order {order_id}: status=failed, failure_reason=unknown. "
        "Unable to determine root cause with available tools. Human investigation required."
    ),
}

_NEXT_STEP_TEMPLATES = {
    "bank_error": (
        "Contact acquiring bank or payment channel ops team with the order ID and PSP reference. "
        "Check for channel-level processing errors in the ops dashboard."
    ),
    "order_expired": (
        "Review refund eligibility policy for this order type. "
        "Determine if a manual override is warranted."
    ),
    "order_not_found": (
        "Verify the order ID in the internal ops system. "
        "Check if the order was created under a different merchant account."
    ),
    "unknown": (
        "Investigate the transaction log for order {order_id}. "
        "Check payment processor error codes."
    ),
}


def build_escalation(state: AgentState) -> dict:
    order_id = state.get("order_id", "unknown")
    failure_reason = state.get("failure_reason_code", "unknown")
    account_status = state.get("account_status", "unknown")

    reasoning = _REASONING_TEMPLATES.get(
        failure_reason,
        _REASONING_TEMPLATES["unknown"],
    ).format(order_id=order_id, account_status=account_status)

    next_step = _NEXT_STEP_TEMPLATES.get(
        failure_reason,
        _NEXT_STEP_TEMPLATES["unknown"],
    ).format(order_id=order_id)

    payload = {
        "session_id": state.get("session_id", ""),
        "merchant_id": state.get("merchant_id", ""),
        "channel": state.get("channel", ""),
        "order_id": order_id,
        "refund_status": state.get("refund_status", "unknown"),
        "failure_reason_code": failure_reason,
        "account_status": account_status,
        "merchant_original_message": state.get("merchant_message", ""),
        "agent_reasoning": reasoning,
        "recommended_next_step": next_step,
        "escalation_reason": f"failure_reason={failure_reason}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Validate required fields
    missing = [f for f in REQUIRED_FIELDS if not payload.get(f)]
    if missing:
        payload["_validation_warning"] = f"missing fields: {missing}"

    merchant_text = render("escalated")

    return {
        "escalation_payload": payload,
        "response_text": merchant_text,
        "messages": [{"role": "assistant", "content": merchant_text}],
    }
