"""
Mock Order / Transaction System API.

In production, replace get_refund_status() with a real HTTP call.
The return schema is the contract — the mock and real connector must match.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class RefundStatusResult:
    order_id: str
    refund_status: Literal["pending", "initiated", "succeeded", "failed", "canceled"]
    pending_reason: str | None       # processing | insufficient_funds | charge_pending
    amount: float
    currency: str
    expected_arrival: str | None     # ISO8601
    account_id: str                  # used to look up account if status == failed
    error: str | None = None


# ── Mock data: covers every branch in the workflow ───────────────────────────

_ORDERS: dict[str, RefundStatusResult] = {
    # Happy paths
    "10248": RefundStatusResult(
        order_id="10248",
        refund_status="pending",
        pending_reason="processing",
        amount=299.00,
        currency="CNY",
        expected_arrival="2026-10-07",
        account_id="ACC-001",
    ),
    "10249": RefundStatusResult(
        order_id="10249",
        refund_status="initiated",
        pending_reason=None,
        amount=599.00,
        currency="CNY",
        expected_arrival="2026-10-05",
        account_id="ACC-002",
    ),
    "10250": RefundStatusResult(
        order_id="10250",
        refund_status="succeeded",
        pending_reason=None,
        amount=199.00,
        currency="CNY",
        expected_arrival=None,
        account_id="ACC-003",
    ),
    # Failed paths — each maps to a different failure_reason_code
    "10251": RefundStatusResult(
        order_id="10251",
        refund_status="failed",
        pending_reason=None,
        amount=899.00,
        currency="CNY",
        expected_arrival=None,
        account_id="ACC-004",   # → insufficient_funds
    ),
    "10252": RefundStatusResult(
        order_id="10252",
        refund_status="failed",
        pending_reason=None,
        amount=1299.00,
        currency="CNY",
        expected_arrival=None,
        account_id="ACC-005",   # → account_frozen
    ),
    "10253": RefundStatusResult(
        order_id="10253",
        refund_status="failed",
        pending_reason=None,
        amount=499.00,
        currency="CNY",
        expected_arrival=None,
        account_id="ACC-006",   # → bank_error → escalate
    ),
    "10254": RefundStatusResult(
        order_id="10254",
        refund_status="failed",
        pending_reason=None,
        amount=149.00,
        currency="CNY",
        expected_arrival=None,
        account_id="ACC-007",   # → order_expired → escalate
    ),
}


def get_refund_status(order_id: str) -> RefundStatusResult:
    """
    Returns refund status for a given order ID.
    Raises KeyError if order not found — caller must handle.
    """
    if order_id not in _ORDERS:
        raise KeyError(f"order_not_found: {order_id}")
    return _ORDERS[order_id]
