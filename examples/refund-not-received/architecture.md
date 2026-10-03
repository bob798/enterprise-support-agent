# Architecture: Refund Not Received

> **Phase:** Design
> **Date:** 2026-10-03
> **Input:** workflow.md — translated into technical components
> **Output:** Component design, tool contracts, data flows, and technology decisions for the agent implementation

---

## System Overview

```
Merchant (IM)
    │
    ▼
[IM Adapter]  ←── 企业微信 / 飞书 / 钉钉 webhook
    │
    ▼
[Agent Orchestrator]
    ├── Intent Classifier
    ├── Information Collector      ←── ask for order number if missing
    ├── Tool: query_refund_status  ←── Order / Transaction System API
    ├── Tool: query_account_info   ←── Account / Balance System API
    ├── Result Router              ←── rule-based, deterministic
    ├── Response Generator         ←── templated + grounded
    └── Escalation Builder         ←── structured handoff payload
              │
              ▼
    [Human Agent Queue]
```

---

## Component Design

### 1. IM Adapter

**Role:** Normalize inbound messages from different IM platforms into a unified format. Route outbound responses back to the correct channel.

**Input:** Raw webhook payload from 企业微信 / 飞书 / 钉钉
**Output:** Normalized message object

```json
{
  "session_id": "string",
  "channel": "wechat_work | feishu | dingtalk",
  "merchant_id": "string",
  "message_text": "string",
  "timestamp": "ISO8601"
}
```

**Note:** Merchant identity is extracted from the IM session binding — no separate auth step required.

---

### 2. Intent Classifier

**Role:** Determine whether the message is a refund status inquiry. Route to the correct workflow.

**Model:** LLM (lightweight — intent classification only)
**Input:** `message_text`
**Output:** `intent` + `extracted_order_id` (nullable)

```json
{
  "intent": "refund_status_inquiry | other",
  "extracted_order_id": "string | null",
  "confidence": 0.0
}
```

**Routing:**
- `intent = refund_status_inquiry` → proceed to Information Collector
- `intent = other` → route to general handler (out of scope for v1)
- `confidence < 0.7` → ask clarifying question before proceeding

---

### 3. Information Collector

**Role:** Ensure all required inputs are present before calling any tool.

**Required fields:**
- `order_id` — extracted from message or collected via follow-up question

**Logic:**
```
if extracted_order_id is not None:
    proceed to query_refund_status(order_id)
else:
    send: "请提供订单号，以便我为您查询退款状态。"
    wait for merchant reply → re-extract order_id → proceed
```

**Max retries:** 2 — after 2 failed extractions, escalate to human.

---

### 4. Tool: query_refund_status

**Role:** Retrieve the current refund status from the Order / Transaction system.

**Type:** Read-only API call
**Requires human approval:** No

**Input:**
```json
{ "order_id": "string" }
```

**Output:**
```json
{
  "order_id": "string",
  "refund_status": "pending | initiated | succeeded | failed | canceled",
  "pending_reason": "processing | insufficient_funds | charge_pending | null",
  "amount": "number",
  "currency": "string",
  "created_at": "ISO8601",
  "expected_arrival": "ISO8601 | null"
}
```

**Error handling:**

| Error | Agent behavior |
|---|---|
| `order_not_found` | Reply: "未找到该订单，请确认订单号是否正确。" |
| `unauthorized` | Escalate to human immediately |
| `timeout` | Retry once; if fails again → escalate |

---

### 5. Tool: query_account_info

**Role:** Retrieve account state and balance when refund status is `failed`.

**Type:** Read-only API call
**Requires human approval:** No

**Input:**
```json
{ "account_id": "string" }
```

**Output:**
```json
{
  "account_id": "string",
  "status": "active | frozen | suspended | closed",
  "balance": "number",
  "currency": "string",
  "risk_flags": ["string"],
  "failure_reason_code": "insufficient_funds | account_frozen | risk_control | bank_error | order_expired | unknown"
}
```

**Error handling:** Same pattern as `query_refund_status`.

---

### 6. Result Router

**Role:** Map tool outputs to one of three actions: direct reply, investigate further, or escalate.

**Type:** Deterministic rule engine — no LLM involved in routing decisions.

```
refund_status = query_refund_status(order_id)

if status in [pending, initiated, succeeded]:
    → Response Generator (standard reply)

if status == failed:
    account = query_account_info(account_id)

    if failure_reason in [insufficient_funds]:
        → Response Generator (balance reply)

    if failure_reason in [account_frozen, risk_control]:
        → Response Generator (frozen reply)

    if failure_reason in [bank_error, order_expired, unknown]:
        → Escalation Builder
```

**Design principle:** Routing is rule-based and deterministic. The LLM is not asked to decide whether to escalate — the rules decide. This eliminates a class of failure where the model underestimates risk.

---

### 7. Response Generator

**Role:** Produce a grounded, merchant-facing reply using tool output data.

**Type:** LLM with strict grounding constraint — every factual claim must reference a tool output field.

**Templates by status:**

| Status / Reason | Template |
|---|---|
| pending | "您的退款正在处理中（订单 {order_id}），预计 {expected_arrival} 到账，请耐心等待。" |
| initiated | "退款已发起，正在等待银行处理，通常需要 3–5 个工作日。" |
| succeeded | "退款已成功（{amount} {currency}），请确认收款方是否已收到。如买家仍未收到，建议联系其开户行核实。" |
| insufficient_funds | "退款失败，原因：账户余额不足（当前余额不足以覆盖退款金额）。请充值后重新发起退款。" |
| account_frozen / risk_control | "退款失败，原因：账户异常（{failure_reason_code}）。请联系运营团队处理账户问题后重新操作。" |

**Constraint:** Template variables must be filled from tool output. If a required field is null or missing, do not infer — escalate instead.

---

### 8. Escalation Builder

**Role:** Assemble a structured handoff payload and route to the human agent queue.

**Trigger conditions:**
- `failure_reason` in `[bank_error, order_expired, unknown]`
- Tool call timeout after retry
- `order_not_found` after merchant confirms order number
- Information Collector fails after 2 retries
- Any unexpected system error

**Handoff payload schema (enhanced from workflow.md):**

```json
{
  "session_id": "string",
  "merchant_id": "string",
  "channel": "string",
  "order_id": "string",
  "refund_status": "string",
  "failure_reason_code": "string",
  "account_status": "string | null",
  "merchant_original_message": "string",
  "agent_reasoning": "string",
  "recommended_next_step": "string",
  "escalation_reason": "string",
  "timestamp": "ISO8601"
}
```

**`agent_reasoning` example:**
> "Queried order TX-8821: status=failed, failure_reason=bank_error. Account status=active, balance sufficient. Root cause requires bank/channel investigation — outside agent scope."

**`recommended_next_step` example:**
> "Contact acquiring bank or payment channel ops team with PSP reference. Check for channel-level processing errors in the ops dashboard."

**Merchant-facing message on escalation:**
> "您的问题需要人工协助处理，我已将详情转交给技术支持团队，预计将在 [SLA] 内与您联系。"

---

## Technology Stack

| Component | Technology | Rationale |
|---|---|---|
| Agent orchestrator | LangGraph / custom Python | Explicit state machine — matches decision tree structure |
| LLM | Claude Haiku (intent) + Claude Sonnet (response generation) | Haiku for low-cost classification; Sonnet for grounded reply |
| IM adapter | Webhook + platform SDK | 企业微信 / 飞书 / 钉钉 each have official bot APIs |
| Tool layer | Python + httpx | Thin HTTP wrappers — no framework overhead needed |
| Order/Transaction API | Mock → real API | Mock for dev/eval; real connector for deployment |
| Account/Balance API | Mock → real API | Same pattern |
| Session state | Redis | IM sessions need short-lived context across turns |
| Escalation queue | Ticketing system webhook | Delivers handoff payload to human agent |
| Observability | LangSmith / OpenTelemetry | Trace every LLM call and tool call |

---

## Data Flow Diagram

```
Merchant ──► IM Adapter ──► Orchestrator
                                │
                    ┌───────────┴──────────────┐
                    │                          │
              Intent Classifier          [session state: Redis]
                    │
              Information Collector
              (ask for order_id if missing)
                    │
              query_refund_status() ◄──── Order/Transaction API
                    │
             ┌──────┴──────┐
           clear          failed
             │               │
      Response Generator  query_account_info() ◄── Account/Balance API
             │               │
           reply         ┌───┴───┐
                       clear   unclear
                         │        │
                  Response    Escalation
                  Generator    Builder ──► Human Queue
                         │        │
                       reply    "转人工" message to merchant
```

---

## Security & Compliance Constraints

| Constraint | Implementation |
|---|---|
| No account write operations | Tool layer has no write methods — enforced at code level |
| PII in responses | Mask account numbers, card details before sending to IM |
| Credentials | All API keys via environment variables — never in code |
| Audit trail | Every tool call logged with session_id, timestamp, input/output |
| Data retention | Session context in Redis with TTL = 24h |

---

## Open Items for Implementation

- [ ] Confirm Order/Transaction API endpoint and auth method
- [ ] Confirm Account/Balance API endpoint and auth method
- [ ] Decide: does agent send reply directly to merchant, or draft for engineer review?
- [ ] Define SLA for human escalation response time
- [ ] Choose IM platform for v1 (single platform first — suggest 企业微信)
- [ ] Confirm `account_id` is derivable from `order_id` without additional lookup
