"""
Tool: query_refund_status

Wraps the Order/Transaction connector.
Read-only. No write operations.
"""

from connectors.mock.order_system import get_refund_status, RefundStatusResult


def query_refund_status(order_id: str) -> dict:
    """
    Returns refund status dict, or error dict on failure.
    Caller must check result["error"] before using other fields.
    """
    try:
        result: RefundStatusResult = get_refund_status(order_id)
        return {
            "order_id": result.order_id,
            "refund_status": result.refund_status,
            "pending_reason": result.pending_reason,
            "amount": result.amount,
            "currency": result.currency,
            "expected_arrival": result.expected_arrival,
            "account_id": result.account_id,
            "error": None,
        }
    except KeyError:
        return {
            "order_id": order_id,
            "refund_status": None,
            "error": "order_not_found",
        }
    except Exception as e:
        return {
            "order_id": order_id,
            "refund_status": None,
            "error": f"api_timeout: {str(e)}",
        }
