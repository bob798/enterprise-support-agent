"""
Node: Result Router (deterministic rule engine)

Maps tool output to next_action.
NO LLM involved — pure rule-based logic.

This is intentional: routing decisions in financial workflows
must be deterministic and auditable, not probabilistic.
Ref: arxiv 2603.01548 — deterministic routing reduces LLM calls by 93%.
"""

from agent.state import AgentState

# Failure reasons that can be communicated directly to the merchant
DIRECT_REPLY_REASONS = {"insufficient_funds", "account_frozen", "risk_control"}

# Failure reasons that require human investigation
ESCALATE_REASONS = {"bank_error", "order_expired", "unknown", "order_not_found"}
ESCALATE_ERROR_PREFIXES = ("api_timeout",)


def route_result(state: AgentState) -> dict:
    refund_status = state.get("refund_status")
    failure_reason = state.get("failure_reason_code")

    # ── API error or order not found ─────────────────────────────────────
    if failure_reason and any(
        failure_reason.startswith(p) for p in ESCALATE_ERROR_PREFIXES
    ):
        return {"next_action": "escalate"}

    if failure_reason == "order_not_found":
        return {"next_action": "error"}

    # ── Clear statuses → direct reply ────────────────────────────────────
    if refund_status in ("pending", "initiated", "succeeded"):
        return {"next_action": "direct_reply"}

    # ── Failed → check failure reason ────────────────────────────────────
    if refund_status == "failed":
        if failure_reason in DIRECT_REPLY_REASONS:
            return {"next_action": "direct_reply"}
        if failure_reason in ESCALATE_REASONS:
            return {"next_action": "escalate"}
        # Unknown failure reason → escalate conservatively
        return {"next_action": "escalate"}

    # ── Fallback ─────────────────────────────────────────────────────────
    return {"next_action": "escalate"}
