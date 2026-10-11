"""
Agent state definition.
Every field is written by exactly one node — prevents hidden coupling.
"""

from typing import Annotated, Literal
from typing_extensions import TypedDict
import operator


class AgentState(TypedDict):
    # ── Session context (set by IM Adapter, never modified) ──────────────
    session_id: str
    merchant_id: str
    channel: Literal["wechat_work", "feishu", "dingtalk", "api"]

    # ── Conversation ──────────────────────────────────────────────────────
    merchant_message: str          # original inbound message
    messages: Annotated[list[dict], operator.add]  # full turn history

    # ── Intent Classifier output ──────────────────────────────────────────
    intent: str                    # refund_status_inquiry | other | unclear
    intent_confidence: float       # 0.0–1.0; < 0.7 → ask for clarification

    # ── Information Collector output ──────────────────────────────────────
    order_id: str | None           # extracted or collected from merchant
    collect_retries: int           # number of times we've asked for order_id

    # ── Tool: query_refund_status output ─────────────────────────────────
    refund_status: str | None      # pending | initiated | succeeded | failed | canceled
    pending_reason: str | None     # processing | insufficient_funds | charge_pending
    refund_amount: float | None
    refund_currency: str | None
    expected_arrival: str | None   # ISO8601 or None

    # ── Tool: query_account_info output ──────────────────────────────────
    account_id: str | None         # set by refund_status tool for account lookup
    account_status: str | None     # active | frozen | suspended | closed
    failure_reason_code: str | None  # insufficient_funds | account_frozen |
                                     # risk_control | bank_error | order_expired | unknown

    # ── Result Router output ──────────────────────────────────────────────
    next_action: Literal[
        "direct_reply",
        "escalate",
        "ask_order_id",
        "ask_clarification",
        "error",
    ] | None

    # ── Response Generator / Escalation Builder output ───────────────────
    response_text: str | None       # text sent back to merchant via IM
    escalation_payload: dict | None # structured handoff for human agent
