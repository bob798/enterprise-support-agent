# Risk Assessment: Refund Not Received

> **Phase:** Design
> **Date:** 2026-10-03
> **Input:** architecture.md — risks identified per component
> **Purpose:** Systematically assess every risk, assign severity, and define concrete mitigations before implementation begins.

---

## Risk Register

| # | Risk | Component | Likelihood | Impact | Score | Status |
|---|---|---|---|---|---|---|
| R1 | Agent returns wrong refund status | query_refund_status | Low | Critical | 8 | Mitigated |
| R2 | Agent communicates wrong result to merchant | Response Generator | Low | Critical | 8 | Mitigated |
| R3 | Merchant stops pursuing real problem due to false "resolved" | Response Generator | Med | Critical | 9 | Mitigated |
| R4 | Agent attempts or suggests account write operations | Result Router | Low | Critical | 8 | Mitigated |
| R5 | Order number extraction returns wrong ID | Intent Classifier | Med | High | 6 | Mitigated |
| R6 | Agent escalates with incomplete context | Escalation Builder | Low | High | 4 | Mitigated |
| R7 | Confidence threshold miscalibrated — agent responds when it should escalate | Intent Classifier | Med | High | 6 | Mitigated |
| R8 | Tool timeout causes silent failure | Tool layer | Med | Med | 4 | Mitigated |
| R9 | PII leaks in IM response | Response Generator | Low | High | 4 | Mitigated |
| R10 | IM webhook spoofing — unauthorized merchant accesses another merchant's data | IM Adapter | Low | Critical | 8 | Mitigated |

_Likelihood: Low=1, Med=2, High=3. Impact: Med=2, High=3, Critical=4. Score = Likelihood × Impact._

---

## Detailed Risk Analysis

### R1 — Wrong refund status returned

**Scenario:** The Order/Transaction API returns stale or incorrect data. The agent passes it through without verification.

**Why critical:** In financial contexts, a wrong status (e.g., "succeeded" when actually "failed") causes the merchant to tell their buyer the money is on the way — creating a customer trust failure downstream.

**Industry validation:** Fini explicitly names this as their primary design constraint: *"a hallucinated refund is a direct financial loss."*

**Mitigations:**
- Agent always cites the raw API response in its reasoning trace
- Response templates include the actual status code, not just a plain-language interpretation
- Evaluation dataset includes cases where API returns edge-case or unexpected values
- **Never** use LLM inference to fill in missing status fields — if status is null, escalate

---

### R2 — Wrong result communicated to merchant

**Scenario:** Even if the tool returns correct data, the Response Generator misinterprets or paraphrases it incorrectly.

**Mitigations:**
- Response templates are parameterized from tool output fields — not free-form LLM generation
- Required fields: `refund_status`, `amount`, `currency` must be present before response is sent
- Grounding check: response is verified to contain no claims not present in tool output
- Eval dimension: factual groundedness ≥ 95% on golden dataset

---

### R3 — False "resolved" causes merchant to stop pursuing real problem

**Scenario:** Agent says "your refund is being processed" when in fact the refund has failed. Merchant stops following up. Buyer never receives money.

**Why this is the highest-scored risk:** This failure is invisible — neither the agent nor the system knows it happened. It surfaces only when the buyer complains again, by which time SLA has been breached.

**Mitigations:**
- Agent must distinguish between "status retrieved" and "problem resolved"
- `succeeded` reply includes: "请确认收款方是否已收到，如仍未到账请再次联系我们"
- `pending`/`initiated` reply includes explicit: "如 {expected_arrival} 后仍未到账，请重新提交工单"
- Agent never uses the word "已解决" / "resolved" unless `refund_status = succeeded` AND merchant confirms receipt

---

### R4 — Agent attempts account write operations

**Scenario:** Merchant asks "can you trigger a re-try on my refund?" Agent attempts to call a write endpoint.

**Mitigation (enforced at code level, not prompt level):**
- Tool layer contains **zero write methods** — no `retry_refund()`, no `update_account()`, no `trigger_payout()`
- If merchant requests a write action, the response is always: "该操作需要人工处理，我已为您提交升级请求。"
- This is a hard architectural boundary, not a guardrail prompt

---

### R5 — Order number extraction returns wrong ID

**Scenario:** Merchant message contains multiple numbers (e.g., "order 10248 and invoice 3391"). Classifier extracts the wrong one.

**Mitigations:**
- If multiple numeric IDs are detected, ask merchant to confirm which is the order number
- After extraction, confirm with merchant: "您是指订单号 {order_id} 吗？"
- If query returns `order_not_found`, ask merchant to re-verify before retrying
- Max 2 retries before escalating

---

### R6 — Escalation with incomplete context

**Scenario:** Agent escalates but handoff payload is missing key fields. Human agent must re-query systems from scratch — losing the time benefit of automation.

**Mitigations:**
- Escalation Builder validates all required fields before sending payload
- If any required field is null, the builder substitutes `"not_retrieved"` with a note, rather than silently omitting
- Required fields: `order_id`, `refund_status`, `failure_reason_code`, `merchant_original_message`, `agent_reasoning`, `recommended_next_step`
- Eval dimension: escalation payload completeness checked in every escalation test case

---

### R7 — Confidence threshold miscalibrated

**Scenario:** Intent classifier is overconfident — routes a non-refund-inquiry into the refund workflow, or misroutes an ambiguous message.

**Mitigations:**
- Threshold default: 0.7. Below threshold → ask clarifying question, do not assume
- Red-team test set: 20 messages that should NOT trigger refund workflow (out-of-scope requests, unrelated questions)
- Threshold tunable per deployment — not hardcoded

---

### R8 — Tool timeout causes silent failure

**Scenario:** Order/Transaction API times out. Agent has no status to report but does not communicate this clearly to the merchant.

**Mitigations:**
- Retry once on timeout (configurable)
- After retry failure: escalate with `failure_reason_code = "api_timeout"`, not a generic error message
- Merchant message: "系统暂时无法查询，已为您提交人工处理请求，请稍候。"
- All timeouts logged with session_id and timestamp for ops monitoring

---

### R9 — PII leaks in IM response

**Scenario:** Account balance, card last four digits, or bank account number appears in a response sent to the merchant's IM.

**Mitigations:**
- Response Generator applies PII mask before sending: account numbers → `****`, card digits → `****`
- Explicit fields to mask: `account_id`, `bank_account_number`, `card_last4`, `balance` (show range, not exact value if sensitive)
- PII masking is applied as a post-processing step — even if template inadvertently includes a raw field

---

### R10 — IM webhook spoofing

**Scenario:** A malicious request mimics a legitimate IM webhook, submitting queries on behalf of a different merchant.

**Mitigations:**
- Validate webhook signature from IM platform on every request
- `merchant_id` is extracted from the authenticated session binding — never from the message body
- All API queries scoped to the authenticated `merchant_id` — no cross-merchant data access possible at tool level

---

## Guardrail Summary

| Guardrail | Type | Enforcement |
|---|---|---|
| No write operations | Architectural | Tool layer has no write methods |
| Grounding check | Output validation | Response must cite tool output fields |
| Confidence gate | Routing | < 0.7 → clarify, not assume |
| PII masking | Output post-processing | Applied before IM send |
| Webhook signature validation | Input validation | Every inbound request |
| Escalation payload validation | Output validation | All required fields present |
| Timeout escalation | Error handling | Retry once → escalate with reason |

---

## Residual Risks (Accepted)

| Risk | Why accepted | Owner |
|---|---|---|
| API returns correct but stale data (caching at source system) | Outside agent's control; mitigated by citing data timestamp in response | Platform / ops team |
| Merchant misunderstands a correct response | Language clarity issue; mitigated by template design and user testing | Product / UX |
