"""
Unit tests: Result Router (agent/nodes/router.py)

Design ref: DESIGN.md §D2 — deterministic routing, no LLM.
Acceptance:  F4 (status routing), F5 (failed→account), F6/F7 (direct reply),
             F8 (escalation triggers)

All tests run without ANTHROPIC_API_KEY.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from tests.conftest import make_state
from agent.nodes.router import route_result


# ── Happy paths: clear statuses → direct_reply ───────────────────────────────

class TestDirectReplyStatuses:
    """F4: pending / initiated / succeeded → direct_reply"""

    def test_pending_routes_direct(self):
        state = make_state(refund_status="pending")
        result = route_result(state)
        assert result["next_action"] == "direct_reply"

    def test_initiated_routes_direct(self):
        state = make_state(refund_status="initiated")
        result = route_result(state)
        assert result["next_action"] == "direct_reply"

    def test_succeeded_routes_direct(self):
        state = make_state(refund_status="succeeded")
        result = route_result(state)
        assert result["next_action"] == "direct_reply"


# ── Failed + communicable reason → direct_reply ───────────────────────────────

class TestFailedDirectReply:
    """F6/F7: failed with reason merchant can act on → direct_reply"""

    def test_insufficient_funds_direct(self):
        state = make_state(refund_status="failed", failure_reason_code="insufficient_funds")
        result = route_result(state)
        assert result["next_action"] == "direct_reply"

    def test_account_frozen_direct(self):
        state = make_state(refund_status="failed", failure_reason_code="account_frozen")
        result = route_result(state)
        assert result["next_action"] == "direct_reply"

    def test_risk_control_direct(self):
        state = make_state(refund_status="failed", failure_reason_code="risk_control")
        result = route_result(state)
        assert result["next_action"] == "direct_reply"


# ── Failed + opaque reason → escalate ────────────────────────────────────────

class TestFailedEscalation:
    """F8: failed with reason requiring human investigation → escalate"""

    def test_bank_error_escalates(self):
        state = make_state(refund_status="failed", failure_reason_code="bank_error")
        result = route_result(state)
        assert result["next_action"] == "escalate"

    def test_order_expired_escalates(self):
        state = make_state(refund_status="failed", failure_reason_code="order_expired")
        result = route_result(state)
        assert result["next_action"] == "escalate"

    def test_unknown_failure_escalates(self):
        state = make_state(refund_status="failed", failure_reason_code="unknown")
        result = route_result(state)
        assert result["next_action"] == "escalate"

    def test_novel_failure_code_escalates_conservatively(self):
        """Any failure reason not in DIRECT_REPLY_REASONS must escalate, not drop silently."""
        state = make_state(refund_status="failed", failure_reason_code="some_new_code_v2")
        result = route_result(state)
        assert result["next_action"] == "escalate"


# ── Order not found → error ───────────────────────────────────────────────────

class TestOrderNotFound:
    def test_order_not_found_routes_error(self):
        state = make_state(failure_reason_code="order_not_found")
        result = route_result(state)
        assert result["next_action"] == "error"


# ── API errors → escalate ─────────────────────────────────────────────────────

class TestApiErrors:
    """S4: timeout escalates with reason, not silent failure"""

    def test_api_timeout_escalates(self):
        state = make_state(failure_reason_code="api_timeout_order")
        result = route_result(state)
        assert result["next_action"] == "escalate"

    def test_api_timeout_prefix_variants_escalate(self):
        for code in ("api_timeout_order", "api_timeout_account", "api_timeout"):
            state = make_state(failure_reason_code=code)
            result = route_result(state)
            assert result["next_action"] == "escalate", f"expected escalate for {code}"


# ── Fallback: no useful state → escalate ─────────────────────────────────────

class TestFallback:
    """Router must never drop a message silently — always escalate if unsure."""

    def test_no_status_escalates(self):
        state = make_state(refund_status=None, failure_reason_code=None)
        result = route_result(state)
        assert result["next_action"] == "escalate"

    def test_unexpected_status_escalates(self):
        state = make_state(refund_status="unknown_status_v3")
        result = route_result(state)
        assert result["next_action"] == "escalate"
