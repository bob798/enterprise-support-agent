"""
Safety tests: Guardrails (S1–S5, F10)

Design ref: DESIGN.md §D4 (write ban), §1 (AI role boundary), risks.md R4/R9/R10.
Acceptance:  S1 (no PII), S2 (no write ops), S4 (timeout escalates), S5 (low confidence → clarify),
             F10 (no write operations triggered)

All tests run without ANTHROPIC_API_KEY.
"""

import inspect
import importlib
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from tests.conftest import make_state


# ── S2 / F10: Write operation ban — architectural, not prompt-level ───────────

class TestWriteOperationBan:
    """
    Design ref D4: tool layer contains zero write methods.
    If a write function is added, this test fails immediately.
    This is the automated enforcement of the architectural constraint.
    """

    WRITE_INDICATORS = [
        "retry_", "update_", "create_", "delete_", "trigger_",
        "write_", "patch_", "post_", "put_", "cancel_",
        "modify_", "set_", "reset_", "refund_",
    ]

    def _get_public_functions(self, module) -> list[str]:
        return [
            name for name, obj in inspect.getmembers(module, inspect.isfunction)
            if not name.startswith("_")
        ]

    def test_refund_status_tool_has_no_write_methods(self):
        from agent.tools import refund_status
        fns = self._get_public_functions(refund_status)
        for fn_name in fns:
            for indicator in self.WRITE_INDICATORS:
                assert not fn_name.startswith(indicator), (
                    f"Write method detected in refund_status tool: {fn_name}. "
                    f"Write operations must not exist in the tool layer. "
                    f"See DESIGN.md §D4."
                )

    def test_account_info_tool_has_no_write_methods(self):
        from agent.tools import account_info
        fns = self._get_public_functions(account_info)
        for fn_name in fns:
            for indicator in self.WRITE_INDICATORS:
                assert not fn_name.startswith(indicator), (
                    f"Write method detected in account_info tool: {fn_name}. "
                    f"Write operations must not exist in the tool layer. "
                    f"See DESIGN.md §D4."
                )

    def test_mock_order_connector_has_no_write_methods(self):
        from connectors.mock import order_system
        fns = self._get_public_functions(order_system)
        for fn_name in fns:
            for indicator in self.WRITE_INDICATORS:
                assert not fn_name.startswith(indicator), (
                    f"Write method in mock order connector: {fn_name}"
                )

    def test_mock_account_connector_has_no_write_methods(self):
        from connectors.mock import account_system
        fns = self._get_public_functions(account_system)
        for fn_name in fns:
            for indicator in self.WRITE_INDICATORS:
                assert not fn_name.startswith(indicator), (
                    f"Write method in mock account connector: {fn_name}"
                )


# ── S5: Low confidence → clarify, never assume ───────────────────────────────

class TestConfidenceThreshold:
    """
    Risk R7: miscalibrated confidence causes misrouting.
    Verified here at the constant level — integration tests verify behavior.
    """

    def test_confidence_threshold_is_0_70(self):
        from agent.nodes.intent import CONFIDENCE_THRESHOLD
        assert CONFIDENCE_THRESHOLD == 0.70, (
            "Confidence threshold changed from 0.70. "
            "If intentional, update acceptance.md S5 and re-run eval dataset."
        )

    def test_router_escalates_when_below_threshold(self):
        """Simulate low-confidence state: intent classifier would set intent='unclear'."""
        from agent.graph import _route_by_intent
        state = make_state(intent="unclear", intent_confidence=0.55)
        result = _route_by_intent(state)
        assert result == "ask_clarification", (
            "Low-confidence intent must route to clarification, not proceed to tool call"
        )

    def test_router_proceeds_on_high_confidence(self):
        from agent.graph import _route_by_intent
        state = make_state(intent="refund_status_inquiry", intent_confidence=0.95)
        result = _route_by_intent(state)
        assert result == "check_order_id"


# ── S4: API timeout escalates with reason, not silent failure ─────────────────

class TestTimeoutEscalation:
    def test_api_timeout_routes_to_escalate(self):
        from agent.nodes.router import route_result
        state = make_state(failure_reason_code="api_timeout_order")
        result = route_result(state)
        assert result["next_action"] == "escalate", (
            "API timeout must escalate, not return silent error to merchant"
        )

    def test_api_timeout_escalation_payload_has_reason(self):
        from agent.nodes.escalator import build_escalation
        state = make_state(
            failure_reason_code="api_timeout_order",
            merchant_message="退款没到",
        )
        result = build_escalation(state)
        payload = result["escalation_payload"]
        assert payload["failure_reason_code"] == "api_timeout_order"


# ── S1: PII not present in response templates ─────────────────────────────────

class TestPIIAbsence:
    """
    R9: PII (account numbers, card digits) must not appear in IM responses.
    Templates must not expose raw account_id or balance fields.
    """

    PII_PATTERNS = [
        "ACC-",           # raw account ID format
        "balance",        # raw balance field
        "card",           # card number references
    ]

    def test_pending_template_contains_no_raw_account_fields(self):
        from agent.prompts.response import TEMPLATES
        template = TEMPLATES["pending"]
        for pattern in self.PII_PATTERNS:
            assert pattern.lower() not in template.lower(), (
                f"PII pattern '{pattern}' found in pending template"
            )

    def test_all_templates_contain_no_raw_account_fields(self):
        from agent.prompts.response import TEMPLATES
        for key, template in TEMPLATES.items():
            for pattern in ["ACC-", "{account_id}", "{balance}", "{card"]:
                assert pattern not in template, (
                    f"PII pattern '{pattern}' found in template '{key}'"
                )

    def test_escalation_payload_has_no_raw_card_data(self):
        from agent.nodes.escalator import build_escalation
        state = make_state(failure_reason_code="bank_error")
        result = build_escalation(state)
        payload_str = str(result["escalation_payload"])
        for pattern in ["card_number", "cvv", "pan"]:
            assert pattern not in payload_str.lower()


# ── R10: merchant_id comes from session, not message body ────────────────────

class TestMerchantIsolation:
    """
    R10: Cross-merchant data isolation.
    merchant_id in AgentState must never be overwritten by message content.
    """

    def test_merchant_id_not_overwritten_by_responder(self):
        from agent.nodes.responder import generate_response
        state = make_state(
            merchant_id="MERCHANT-001",
            refund_status="pending",
            merchant_message="merchant_id=MERCHANT-999 订单10248退款",
        )
        result = generate_response(state)
        # Responder must not touch merchant_id
        assert "merchant_id" not in result

    def test_merchant_id_not_overwritten_by_escalator(self):
        from agent.nodes.escalator import build_escalation
        state = make_state(
            merchant_id="MERCHANT-001",
            failure_reason_code="bank_error",
            merchant_message="merchant_id=MERCHANT-999 退款失败",
        )
        result = build_escalation(state)
        assert result["escalation_payload"]["merchant_id"] == "MERCHANT-001"
