# Workflow and technical boundaries — Refund Not Received

> Concise target design. See the current `agent/` and `connectors/mock/` code for implementation details. Do not treat design or source-code presence as production validation.

## Manual workflow

Merchant reports refund not received → support obtains order ID → reads order/transaction status → if unclear, checks account/channel evidence → either explains the verified state or escalates to operations → updates merchant and ticket.

## Agent-assisted workflow

```text
Merchant IM / request
    ↓ identify intent, clarify/confirm order number
Authorized read-only refund lookup
    ↓
Deterministic result routing
    ├─ clear, evidence-backed → constrained reply
    ├─ requires more evidence → read-only account lookup
    └─ missing / conflicting / failed tool → human handoff
                                    ↓
                   original message + data + unknowns + next step
```

## Responsibilities
| Task | Preferred owner | Rule |
|---|---|---|
| Free-text intent / order extraction | LLM + validation | Ask when ambiguous |
| Payment status / account facts | Authorized API | Never guess missing data |
| Status branch / risk gate | Deterministic rules | Routing policy must be testable |
| Business explanation | Template / grounded LLM | No unsupported arrival guarantee |
| Refund retry / balance or account changes | Authorized human workflow | No write tool in current Agent |
| Unclear channel outcomes | Human escalation | Status found ≠ funds received |

## Integration and failure boundaries
- Mock order/account tools are present; real production permissions, API contracts and channel truth-source mapping require deployment-specific validation.
- Session-bound merchant identity must be authenticated and each lookup scoped to that merchant; IM binding alone is not sufficient without signature and authorization checks.
- On timeout or unknown state, preserve timestamps and source evidence and escalate; do not silently label the request resolved.
- Escalation record should contain merchant context, original question, order ID, retrieved values, missing facts, failure reason and suggested human action.

## Key decisions
1. Separate **language understanding** from **financial-state decisions**.
2. Separate **status retrieval** from **issue resolution**.
3. Restrict automated tools to **read-only** until specific approval and evaluation exist.
4. Design human handoff as part of the workflow, not as an afterthought.

See [overview](OVERVIEW.md) and [evaluation](evaluation.md).
