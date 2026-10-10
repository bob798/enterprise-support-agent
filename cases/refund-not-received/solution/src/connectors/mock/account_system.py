"""
Mock Account / Balance System API.

In production, replace get_account_info() with a real HTTP call.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class AccountInfoResult:
    account_id: str
    status: Literal["active", "frozen", "suspended", "closed"]
    balance: float
    currency: str
    failure_reason_code: Literal[
        "insufficient_funds",
        "account_frozen",
        "risk_control",
        "bank_error",
        "order_expired",
        "unknown",
    ]
    error: str | None = None


_ACCOUNTS: dict[str, AccountInfoResult] = {
    "ACC-004": AccountInfoResult(
        account_id="ACC-004",
        status="active",
        balance=0.00,
        currency="CNY",
        failure_reason_code="insufficient_funds",
    ),
    "ACC-005": AccountInfoResult(
        account_id="ACC-005",
        status="frozen",
        balance=5000.00,
        currency="CNY",
        failure_reason_code="account_frozen",
    ),
    "ACC-006": AccountInfoResult(
        account_id="ACC-006",
        status="active",
        balance=8000.00,
        currency="CNY",
        failure_reason_code="bank_error",
    ),
    "ACC-007": AccountInfoResult(
        account_id="ACC-007",
        status="active",
        balance=2000.00,
        currency="CNY",
        failure_reason_code="order_expired",
    ),
}


def get_account_info(account_id: str) -> AccountInfoResult:
    if account_id not in _ACCOUNTS:
        raise KeyError(f"account_not_found: {account_id}")
    return _ACCOUNTS[account_id]
