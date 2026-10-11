"""
Tool: query_account_info

Wraps the Account/Balance connector.
Read-only. No write operations.
"""

from connectors.mock.account_system import get_account_info, AccountInfoResult


def query_account_info(account_id: str) -> dict:
    try:
        result: AccountInfoResult = get_account_info(account_id)
        return {
            "account_id": result.account_id,
            "account_status": result.status,
            "balance": result.balance,
            "currency": result.currency,
            "failure_reason_code": result.failure_reason_code,
            "error": None,
        }
    except KeyError:
        return {
            "account_id": account_id,
            "account_status": None,
            "failure_reason_code": "unknown",
            "error": "account_not_found",
        }
    except Exception as e:
        return {
            "account_id": account_id,
            "account_status": None,
            "failure_reason_code": "unknown",
            "error": f"api_timeout: {str(e)}",
        }
