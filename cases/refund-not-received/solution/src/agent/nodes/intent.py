"""
Node: Intent Classifier

Classifies inbound message and extracts order_id if present.
Uses Claude Haiku for low cost and fast latency.

Mock mode: set LLM_MODE=mock (or leave ANTHROPIC_API_KEY unset) to run
without a real API key. Mock uses regex heuristics — suitable for demos
and local development. Same interface as the real classifier (D7 pattern).
"""

import json
import os
import re
from anthropic import Anthropic
from agent.state import AgentState
from agent.prompts.intent import INTENT_SYSTEM, INTENT_USER

CONFIDENCE_THRESHOLD = 0.70

# Mock mode when no API key or LLM_MODE=mock
_USE_MOCK = os.environ.get("LLM_MODE", "").lower() == "mock" or \
            not os.environ.get("ANTHROPIC_API_KEY", "").strip()

_client = None if _USE_MOCK else Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Refund-related keywords for mock classifier
_REFUND_KEYWORDS = ["退款", "refund", "没到", "未到账", "退钱", "退回", "到账"]


def _mock_classify(message: str) -> dict:
    """
    Rule-based fallback classifier for demo/dev without API key.
    Detects refund intent by keywords; extracts first 4-6 digit number as order_id.
    """
    text = message.lower()
    is_refund = any(kw in text for kw in _REFUND_KEYWORDS)

    order_id = None
    # \b fails in Python 3 with Chinese text (汉字 is \w).
    # Use negative lookahead/lookbehind on digits instead.
    match = re.search(r"(?<!\d)(\d{4,6})(?!\d)", message)
    if match:
        order_id = match.group(1)

    intent = "refund_status_inquiry" if is_refund else "other"
    raw = json.dumps({"intent": intent, "confidence": 0.92, "extracted_order_id": order_id,
                      "_mock": True})
    return {"intent": intent, "intent_confidence": 0.92, "order_id": order_id,
            "messages": [{"role": "classifier", "content": raw}]}


def classify_intent(state: AgentState) -> dict:
    message = state["merchant_message"]

    if _USE_MOCK:
        return _mock_classify(message)

    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=INTENT_SYSTEM,
        messages=[{"role": "user", "content": INTENT_USER.format(message=message)}],
    )

    raw = response.content[0].text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    result = json.loads(raw)

    intent = result.get("intent", "other")
    confidence = float(result.get("confidence", 0.0))
    order_id = result.get("extracted_order_id")

    if confidence < CONFIDENCE_THRESHOLD:
        intent = "unclear"

    return {
        "intent": intent,
        "intent_confidence": confidence,
        "order_id": order_id,
        "messages": [{"role": "classifier", "content": raw}],
    }
