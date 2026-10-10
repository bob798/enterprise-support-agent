"""
Shared fixtures and helpers for the test suite.

Design note: make_state() builds a minimal valid AgentState dict.
All tests use keyword overrides to express only what they care about.
This avoids re-stating all 20+ fields in every test.
"""

import os
import pytest


# ── State factory ─────────────────────────────────────────────────────────────

def make_state(**overrides) -> dict:
    """Return a minimal valid AgentState dict with safe defaults."""
    base = {
        "session_id": "test-session-001",
        "merchant_id": "MERCHANT-001",
        "channel": "api",
        "merchant_message": "我的退款还没到账",
        "messages": [],
        "intent": "refund_status_inquiry",
        "intent_confidence": 0.95,
        "order_id": "10248",
        "collect_retries": 0,
        "refund_status": None,
        "pending_reason": None,
        "refund_amount": 299.00,
        "refund_currency": "CNY",
        "expected_arrival": "2026-10-07",
        "account_status": None,
        "failure_reason_code": None,
        "next_action": None,
        "response_text": None,
        "escalation_payload": None,
    }
    base.update(overrides)
    return base


# ── Markers ───────────────────────────────────────────────────────────────────

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: requires ANTHROPIC_API_KEY — skip in CI without credentials",
    )


@pytest.fixture
def has_api_key() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))
