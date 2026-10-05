"""
Node: Tool Execution

Calls query_refund_status and (conditionally) query_account_info.
All state mutations from tool output happen here.
"""

from agent.state import AgentState
from agent.tools.refund_status import query_refund_status
from agent.tools.account_info import query_account_info


def run_refund_status(state: AgentState) -> dict:
    order_id = state["order_id"]
    result = query_refund_status(order_id)

    updates: dict = {
        "refund_status": result.get("refund_status"),
        "pending_reason": result.get("pending_reason"),
        "refund_amount": result.get("amount"),
        "refund_currency": result.get("currency"),
        "expected_arrival": result.get("expected_arrival"),
        "messages": [{"role": "tool:refund_status", "content": str(result)}],
    }

    # Store account_id for potential account lookup
    if result.get("account_id"):
        updates["account_id"] = result["account_id"]

    if result.get("error"):
        updates["failure_reason_code"] = result["error"]

    return updates


def run_account_info(state: AgentState) -> dict:
    account_id = state.get("account_id") or ""
    result = query_account_info(account_id)

    return {
        "account_status": result.get("account_status"),
        "failure_reason_code": result.get("failure_reason_code"),
        "messages": [{"role": "tool:account_info", "content": str(result)}],
    }
