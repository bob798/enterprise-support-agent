"""
FastAPI entry point.

POST /chat     — main agent endpoint
GET  /health   — liveness check
GET  /demo     — run all demo scenarios and return results
"""

import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from agent.graph import agent

app = FastAPI(title="Enterprise Support Agent", version="0.1.0")


class ChatRequest(BaseModel):
    message: str
    merchant_id: str = "MERCHANT-001"
    channel: str = "api"
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    response: str
    escalated: bool
    escalation_payload: dict | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    initial_state = {
        "session_id": session_id,
        "merchant_id": req.merchant_id,
        "channel": req.channel,
        "merchant_message": req.message,
        "messages": [{"role": "merchant", "content": req.message}],
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

    result = agent.invoke(initial_state)

    return ChatResponse(
        session_id=session_id,
        response=result.get("response_text", "系统错误，请稍后重试。"),
        escalated=result.get("escalation_payload") is not None,
        escalation_payload=result.get("escalation_payload"),
    )


@app.get("/demo")
def demo():
    """Run all demo scenarios. Useful for quick smoke testing."""
    scenarios = [
        ("退款处理中",       "订单10248的退款还没到账"),
        ("退款已发起",       "10249的退款什么时候到"),
        ("退款已成功",       "我的订单10250退款到了吗"),
        ("余额不足",        "订单号10251退款失败了"),
        ("账户冻结",        "10252退款一直没到，订单10252"),
        ("银行渠道异常→升级", "退款没到，订单10253"),
        ("订单已过期→升级",  "10254退款失败"),
        ("未提供订单号",     "我的退款还没到账"),
        ("订单不存在",      "订单99999退款在哪"),
    ]

    results = []
    for label, message in scenarios:
        resp = chat(ChatRequest(message=message))
        results.append({
            "scenario": label,
            "input": message,
            "response": resp.response[:80] + "..." if len(resp.response) > 80 else resp.response,
            "escalated": resp.escalated,
        })

    return {"demo_results": results}
