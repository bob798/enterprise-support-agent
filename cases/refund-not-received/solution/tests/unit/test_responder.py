"""
Unit tests: Response Generator + Templates (agent/nodes/responder.py, agent/prompts/response.py)

Design ref: DESIGN.md §D3 — template responses, no LLM inference on financial data.
Acceptance:  F4 (correct status reply), F6/F7 (direct reply content),
             R2 (wrong result communication), R3 (false "resolved")

All tests run without ANTHROPIC_API_KEY.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from tests.conftest import make_state
from agent.nodes.responder import (
    generate_response,
    generate_ask_order_id,
    generate_ask_clarification,
    generate_order_not_found,
)
from agent.prompts.response import render, TEMPLATES


# ── Templates render without raising ─────────────────────────────────────────

class TestTemplateRender:
    """Every template must render to a non-empty string with valid kwargs."""

    def test_all_template_keys_render(self):
        kwargs = dict(
            order_id="10248",
            amount=299.00,
            currency="CNY",
            expected_arrival="2026-10-07",
        )
        for key in TEMPLATES:
            text = render(key, **kwargs)
            assert isinstance(text, str)
            assert len(text) > 10, f"template '{key}' rendered to empty/short string"

    def test_missing_key_falls_back_to_error(self):
        text = render("nonexistent_key_xyz")
        assert text == render("error")

    def test_partial_kwargs_does_not_raise(self):
        """render() must not crash if optional fields missing — returns template as-is."""
        text = render("ask_order_id")
        assert "订单号" in text


# ── Order ID is cited in financial replies ────────────────────────────────────

class TestOrderIdGrounding:
    """
    Design ref D3: every financial response must cite the order_id from state.
    Prevents hallucinated order references.
    """

    @pytest.mark.parametrize("status,failure_reason", [
        ("pending", None),
        ("initiated", None),
        ("succeeded", None),
        ("failed", "insufficient_funds"),
        ("failed", "account_frozen"),
        ("failed", "risk_control"),
    ])
    def test_order_id_present_in_direct_reply(self, status, failure_reason):
        state = make_state(
            refund_status=status,
            failure_reason_code=failure_reason,
            order_id="10248",
        )
        result = generate_response(state)
        assert "10248" in result["response_text"], (
            f"order_id missing from response for status={status}, reason={failure_reason}"
        )


# ── R3 guard: succeeded template must not imply problem is resolved ──────────

class TestR3Guard:
    """
    R3 (score 9): False "resolved" causes merchant to stop pursuing real issue.
    The succeeded template must instruct merchant to confirm receipt.
    """

    def test_succeeded_reply_includes_confirmation_prompt(self):
        state = make_state(refund_status="succeeded")
        result = generate_response(state)
        text = result["response_text"]
        # Must include language prompting merchant to verify receipt
        assert any(kw in text for kw in ["确认", "收到", "联系"]), (
            "succeeded reply must prompt merchant to confirm buyer received funds"
        )

    def test_pending_reply_includes_recontact_instruction(self):
        state = make_state(
            refund_status="pending",
            expected_arrival="2026-10-07",
        )
        result = generate_response(state)
        text = result["response_text"]
        # Must include what to do if not received by deadline
        assert any(kw in text for kw in ["未到账", "联系", "工单", "重新"]), (
            "pending reply must tell merchant what to do if funds don't arrive"
        )


# ── Responder node output shape ───────────────────────────────────────────────

class TestResponderOutput:
    def test_generates_response_text_field(self):
        state = make_state(refund_status="pending")
        result = generate_response(state)
        assert "response_text" in result
        assert result["response_text"]

    def test_appends_to_messages(self):
        state = make_state(refund_status="pending")
        result = generate_response(state)
        assert "messages" in result
        assert result["messages"][0]["role"] == "assistant"

    def test_ask_order_id_output(self):
        state = make_state(order_id=None)
        result = generate_ask_order_id(state)
        assert result["response_text"]
        assert "订单" in result["response_text"]

    def test_ask_clarification_output(self):
        state = make_state()
        result = generate_ask_clarification(state)
        assert result["response_text"]

    def test_order_not_found_cites_order_id(self):
        state = make_state(order_id="99999")
        result = generate_order_not_found(state)
        assert "99999" in result["response_text"]

    def test_unknown_status_returns_error_text(self):
        state = make_state(refund_status="totally_unknown")
        result = generate_response(state)
        assert result["response_text"]  # must not raise or return None
