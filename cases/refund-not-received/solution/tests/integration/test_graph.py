"""
Integration tests: Full agent graph with mock connectors + real Claude API.

Design ref: DESIGN.md §D1 (graph topology), §D2 (deterministic routing).
Acceptance:  F1–F10, NF4 (tool call success rate ≥ 99%)

Requires: ANTHROPIC_API_KEY set in environment.
Run with: pytest tests/integration/ -v
Skip in CI: pytest tests/unit/ tests/safety/ (no API key required)
"""

import os
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

pytestmark = pytest.mark.integration

# Skip entire module if no API key
if not os.environ.get("ANTHROPIC_API_KEY"):
    pytest.skip(
        "ANTHROPIC_API_KEY not set — skipping integration tests",
        allow_module_level=True,
    )


from agent.graph import agent


def run(message: str, order_id_in_message: bool = True) -> dict:
    """Helper: invoke agent with a single merchant message."""
    state = {
        "session_id": "integration-test",
        "merchant_id": "MERCHANT-001",
        "channel": "api",
        "merchant_message": message,
        "messages": [{"role": "merchant", "content": message}],
        "intent": "",
        "intent_confidence": 0.0,
        "order_id": None,
        "collect_retries": 0,
        "refund_status": None,
        "pending_reason": None,
        "refund_amount": None,
        "refund_currency": None,
        "expected_arrival": None,
        "account_status": None,
        "failure_reason_code": None,
        "next_action": None,
        "response_text": None,
        "escalation_payload": None,
    }
    return agent.invoke(state)


# ── F4: Clear status replies ──────────────────────────────────────────────────

class TestClearStatuses:
    def test_pending_direct_reply(self):
        result = run("订单10248的退款还没到账")
        assert result["response_text"]
        assert result["escalation_payload"] is None
        assert "处理中" in result["response_text"] or "pending" in result["response_text"].lower()

    def test_initiated_direct_reply(self):
        result = run("10249的退款什么时候到")
        assert result["response_text"]
        assert result["escalation_payload"] is None
        assert "已发起" in result["response_text"] or "10249" in result["response_text"]

    def test_succeeded_direct_reply(self):
        result = run("我的订单10250退款到了吗")
        assert result["response_text"]
        assert result["escalation_payload"] is None
        assert "成功" in result["response_text"] or "已完成" in result["response_text"]


# ── F6/F7: Failed + direct reply reasons ────────────────────────────────────

class TestFailedDirectReply:
    def test_insufficient_funds_direct_reply(self):
        result = run("订单号10251退款失败了")
        assert result["response_text"]
        assert result["escalation_payload"] is None
        assert "余额" in result["response_text"] or "充值" in result["response_text"]

    def test_account_frozen_direct_reply(self):
        result = run("10252退款一直没到，订单10252")
        assert result["response_text"]
        assert result["escalation_payload"] is None
        assert "冻结" in result["response_text"] or "异常" in result["response_text"]


# ── F8: Failed + escalation triggers ────────────────────────────────────────

class TestEscalationTriggers:
    def test_bank_error_escalates(self):
        result = run("退款没到，订单10253")
        assert result["escalation_payload"] is not None
        payload = result["escalation_payload"]
        assert payload["failure_reason_code"] == "bank_error"

    def test_order_expired_escalates(self):
        result = run("10254退款失败")
        assert result["escalation_payload"] is not None
        payload = result["escalation_payload"]
        assert payload["failure_reason_code"] == "order_expired"


# ── F2: Missing order number → ask for it ────────────────────────────────────

class TestMissingOrderNumber:
    def test_asks_for_order_id_when_missing(self):
        result = run("我的退款还没到账", order_id_in_message=False)
        assert result["response_text"]
        assert result["escalation_payload"] is None
        # Should ask for order number
        assert any(kw in result["response_text"] for kw in ["订单号", "订单", "单号"])

    def test_no_tool_call_without_order_id(self):
        """Agent must not attempt a tool call when order_id is absent."""
        result = run("我的退款还没到账")
        # If no order_id extracted, refund_status stays None
        if result.get("order_id") is None:
            assert result.get("refund_status") is None


# ── F9: Escalation payload completeness ──────────────────────────────────────

REQUIRED_FIELDS = [
    "order_id", "refund_status", "failure_reason_code",
    "merchant_original_message", "agent_reasoning", "recommended_next_step",
]

class TestEscalationPayloadCompleteness:
    @pytest.mark.parametrize("message,order_id", [
        ("退款没到，订单10253", "10253"),
        ("10254退款失败", "10254"),
    ])
    def test_all_required_fields_present(self, message, order_id):
        result = run(message)
        assert result["escalation_payload"] is not None, (
            f"Expected escalation for {order_id} but got direct reply"
        )
        payload = result["escalation_payload"]
        for field in REQUIRED_FIELDS:
            assert payload.get(field), (
                f"Required field '{field}' missing from escalation payload for order {order_id}"
            )


# ── Order not found ───────────────────────────────────────────────────────────

class TestOrderNotFound:
    def test_nonexistent_order_returns_not_found(self):
        result = run("订单99999退款在哪")
        assert result["response_text"]
        assert any(kw in result["response_text"] for kw in ["未找到", "不存在", "确认", "99999"])


# ── F1: Intent classification accuracy (spot check) ─────────────────────────

class TestIntentClassification:
    def test_refund_inquiry_classified_correctly(self):
        result = run("订单10248退款还没到")
        # If intent was classified correctly, graph proceeds to tool call
        assert result.get("intent") == "refund_status_inquiry" or result.get("refund_status") is not None

    def test_out_of_scope_does_not_trigger_tool_call(self):
        result = run("你们的营业时间是几点")
        # Should ask for clarification, not call refund tool
        assert result["escalation_payload"] is None
        assert result.get("refund_status") is None
