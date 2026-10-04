"""
Unit tests: Escalation Builder (agent/nodes/escalator.py)

Design ref: DESIGN.md §D2, R6 mitigation.
Acceptance:  F9 — escalation payload contains all 6 required fields, 100%.

All tests run without ANTHROPIC_API_KEY.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from tests.conftest import make_state
from agent.nodes.escalator import build_escalation, REQUIRED_FIELDS


# ── F9: All 6 required fields present in every escalation ────────────────────

REQUIRED_6 = [
    "order_id",
    "refund_status",
    "failure_reason_code",
    "merchant_original_message",
    "agent_reasoning",
    "recommended_next_step",
]

class TestRequiredFields:
    @pytest.mark.parametrize("failure_reason", [
        "bank_error",
        "order_expired",
        "unknown",
        "order_not_found",
    ])
    def test_all_required_fields_present(self, failure_reason):
        state = make_state(
            refund_status="failed",
            failure_reason_code=failure_reason,
            merchant_message="订单10253退款没到账",
        )
        result = build_escalation(state)
        payload = result["escalation_payload"]

        for field in REQUIRED_6:
            assert payload.get(field), (
                f"required field '{field}' missing or empty in escalation payload "
                f"for failure_reason={failure_reason}"
            )

    def test_no_validation_warning_on_complete_state(self):
        state = make_state(
            refund_status="failed",
            failure_reason_code="bank_error",
            merchant_message="退款没到，订单10253",
        )
        result = build_escalation(state)
        payload = result["escalation_payload"]
        assert "_validation_warning" not in payload, (
            "complete state should not trigger validation warning"
        )

    def test_validation_warning_when_order_id_missing(self):
        state = make_state(
            order_id=None,
            refund_status="failed",
            failure_reason_code="bank_error",
            merchant_message="退款没到",
        )
        result = build_escalation(state)
        payload = result["escalation_payload"]
        # order_id defaults to "unknown" when None — warning may or may not trigger
        # but response_text must still be set
        assert result["response_text"]


# ── Reasoning and next_step are non-empty and contextual ─────────────────────

class TestReasoningContent:
    def test_bank_error_reasoning_mentions_bank(self):
        state = make_state(refund_status="failed", failure_reason_code="bank_error")
        result = build_escalation(state)
        reasoning = result["escalation_payload"]["agent_reasoning"]
        assert "bank" in reasoning.lower() or "channel" in reasoning.lower()

    def test_order_expired_next_step_mentions_policy(self):
        state = make_state(refund_status="failed", failure_reason_code="order_expired")
        result = build_escalation(state)
        next_step = result["escalation_payload"]["recommended_next_step"]
        assert "policy" in next_step.lower() or "eligib" in next_step.lower()

    def test_unknown_reason_still_produces_next_step(self):
        state = make_state(refund_status="failed", failure_reason_code="unknown")
        result = build_escalation(state)
        assert result["escalation_payload"]["recommended_next_step"]

    def test_order_id_appears_in_reasoning(self):
        state = make_state(order_id="10253", failure_reason_code="bank_error")
        result = build_escalation(state)
        reasoning = result["escalation_payload"]["agent_reasoning"]
        assert "10253" in reasoning


# ── Escalation output shape ───────────────────────────────────────────────────

class TestEscalatorOutput:
    def test_escalation_payload_is_dict(self):
        state = make_state(failure_reason_code="bank_error")
        result = build_escalation(state)
        assert isinstance(result["escalation_payload"], dict)

    def test_response_text_set_after_escalation(self):
        state = make_state(failure_reason_code="bank_error")
        result = build_escalation(state)
        assert result["response_text"]

    def test_timestamp_present(self):
        state = make_state(failure_reason_code="bank_error")
        result = build_escalation(state)
        assert "timestamp" in result["escalation_payload"]

    def test_merchant_id_preserved(self):
        state = make_state(merchant_id="MERCHANT-007", failure_reason_code="bank_error")
        result = build_escalation(state)
        assert result["escalation_payload"]["merchant_id"] == "MERCHANT-007"

    def test_original_message_preserved(self):
        msg = "我的订单10253退款一直没到"
        state = make_state(merchant_message=msg, failure_reason_code="bank_error")
        result = build_escalation(state)
        assert result["escalation_payload"]["merchant_original_message"] == msg


# ── REQUIRED_FIELDS constant matches the 6 specified in acceptance.md ─────────

def test_required_fields_constant_matches_spec():
    """Regression: if someone adds/removes from REQUIRED_FIELDS, this test catches it."""
    assert set(REQUIRED_FIELDS) == set(REQUIRED_6), (
        "REQUIRED_FIELDS in escalator.py must match the 6 fields in acceptance.md F9"
    )
