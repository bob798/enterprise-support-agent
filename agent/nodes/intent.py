"""
Node: Intent Classifier

Classifies inbound message and extracts order_id if present.
Uses Claude Haiku for low cost and fast latency.
"""

import json
import os
from anthropic import Anthropic
from agent.state import AgentState
from agent.prompts.intent import INTENT_SYSTEM, INTENT_USER

_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
CONFIDENCE_THRESHOLD = 0.70


def classify_intent(state: AgentState) -> dict:
    message = state["merchant_message"]

    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=INTENT_SYSTEM,
        messages=[{"role": "user", "content": INTENT_USER.format(message=message)}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    result = json.loads(raw)

    intent = result.get("intent", "other")
    confidence = float(result.get("confidence", 0.0))
    order_id = result.get("extracted_order_id")

    # Route unclear cases to clarification
    if confidence < CONFIDENCE_THRESHOLD:
        intent = "unclear"

    return {
        "intent": intent,
        "intent_confidence": confidence,
        "order_id": order_id,
        "messages": [{"role": "classifier", "content": raw}],
    }
