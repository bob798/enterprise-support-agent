# Workflow Map: Refund Not Received

> **Phase:** Discover → Design input
> **Date:** 2026-10-03
> **Source:** Interview with payment industry technical support practitioner
> **Purpose:** Map the current manual workflow and identify AI intervention points for agent design.

---

## Channel Context

| Dimension | Detail |
|---|---|
| Primary channel | IM (domestic: 企业微信 / 飞书 / 钉钉) |
| Input format | Free text — order number not guaranteed |
| Identity verification | Not required — IM channel is pre-bound to merchant account |
| Initiator | B2B merchant (not end consumer) |

---

## Workflow Map

```
[Merchant sends IM message]
        │
        ▼
[1. Parse message]
  Contains order number?
        │
   No ──┼── Yes
        │         │
        ▼         │
[1a. Ask merchant   │
  for order number] │
        │           │
        └─────┬─────┘
              │
              ▼
[2. Query Order / Transaction System]
   refund_status = query(order_id)
              │
     ┌────────┼────────────┐
     │        │            │
  pending  initiated    success
     │        │            │
     ▼        ▼            ▼
[3a. Reply:  [3b. Reply:  [3c. Reply:
"Processing, "Initiated,  "Refund sent,
 ETA X days"] awaiting    confirm with
              bank"]       buyer"]
                                        failed
                                           │
                                           ▼
                              [4. Query Account / Balance System]
                               failure_reason = query(account_id)
                                           │
                  ┌────────────────────────┼──────────────────────┐
                  │                        │                       │
          insufficient_balance    account_frozen /        bank_error /
                  │               risk_control             order_expired
                  │                        │                       │
                  ▼                        ▼                       ▼
         [5a. Reply:             [5b. Reply:             [5c. Escalate
          "Insufficient           "Account frozen /        to human]
          balance, please         risk control
          top up and retry"]      triggered,
                                  contact ops"]
                                                                   │
                                                                   ▼
                                                    [6. Handoff payload assembled]
                                                    - order_id
                                                    - refund_status
                                                    - failure_reason_code
                                                    - merchant_original_message
                                                                   │
                                                                   ▼
                                                    [7. Human agent takes over]
```

---

## Step-by-Step Table

| Step | Actor | System | Input | Output | AI handles? |
|---|---|---|---|---|---|
| 1. Parse message | Agent | — | Free text IM | Order number extracted / missing | Yes |
| 1a. Request order number | Agent | IM | Missing order number | Ask merchant | Yes |
| 2. Query refund status | Agent | Order / Transaction system | order_id | refund_status | Yes (tool call) |
| 3a. Reply: pending | Agent | IM | status = pending | Standard reply with ETA | Yes |
| 3b. Reply: initiated | Agent | IM | status = initiated | Standard reply | Yes |
| 3c. Reply: success | Agent | IM | status = success | Standard reply, prompt buyer confirmation | Yes |
| 4. Query account / balance | Agent | Account / Balance system | account_id | failure_reason | Yes (tool call) |
| 5a. Reply: insufficient balance | Agent | IM | reason = balance | Direct reply with action guidance | Yes |
| 5b. Reply: frozen / risk control | Agent | IM | reason = frozen | Direct reply, advise contact ops | Yes |
| 5c. Escalate: bank / channel error | Agent | Ticketing system | reason = bank_error | Handoff payload to human | Yes (escalate) |
| 5c. Escalate: order status invalid | Agent | Ticketing system | reason = order_expired | Handoff payload to human | Yes (escalate) |
| 6. Assemble handoff payload | Agent | — | All collected context | Structured handoff | Yes |
| 7. Human agent resolves | Human | — | Handoff payload | Resolution | No |

---

## Decision Points

| Decision | Condition | Branch |
|---|---|---|
| Has order number? | Extracted from IM message | Yes → query; No → ask |
| Refund status | pending / initiated / success / failed | Direct reply or investigate |
| Failure reason | balance / frozen / bank_error / order_expired | Direct reply or escalate |

---

## AI Intervention Map

| Step | AI role | Boundary |
|---|---|---|
| Parse + extract order number | NLP extraction from free text | Must confirm with merchant if ambiguous |
| Query order status | Tool call (read-only) | Never infer — always call API |
| Classify result and route | Rule-based routing on status value | Deterministic, not probabilistic |
| Query account details | Tool call (read-only) | Never infer — always call API |
| Generate standard replies | Template + grounded data | No fabrication; cite tool output |
| Assemble escalation payload | Structured data aggregation | Include all 4 fields; never drop context |
| **Account write operations** | **Not handled by agent** | **Hard boundary — human only** |

---

## Handoff Payload Schema

When escalating to a human agent, the following fields are always included:

```json
{
  "order_id": "string",
  "refund_status": "failed",
  "failure_reason_code": "string",
  "merchant_original_message": "string"
}
```

This ensures the human agent does not need to re-query systems already checked.

---

## Cases Fully Automated (No Human Required)

| Scenario | Agent action |
|---|---|
| Status: pending | Reply with processing status and ETA |
| Status: initiated | Reply confirming initiation, awaiting bank |
| Status: success | Reply confirming completion, prompt buyer check |
| Status: failed — insufficient balance | Reply with cause and action (top up + retry) |
| Status: failed — account frozen / risk control | Reply with cause, advise merchant to contact ops |

---

## Cases Requiring Human Escalation

| Scenario | Reason |
|---|---|
| Status: failed — bank / channel error | Requires ops-level investigation of payment channel |
| Status: failed — order status invalid | Requires policy review (refund eligibility, expiry) |
| Any ambiguous or multi-system state | Agent cannot determine root cause with available tools |

---

## Notes for Agent Design

1. **Order number extraction must have a fallback.** If extraction fails or is ambiguous, ask — do not guess.
2. **All status values must come from tool output.** No inference, no default assumptions.
3. **Standard replies are templated but include live data** (actual status, actual reason code). Not hardcoded strings.
4. **Escalation is not a failure.** The agent should escalate cleanly with full context, not apologize or leave the merchant without a next step.
5. **The agent never tells the merchant what action it is taking on their account.** It only reports what it found.
