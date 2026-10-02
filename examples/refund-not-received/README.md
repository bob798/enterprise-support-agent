# Example: Refund Not Received

> **Status:** In progress
> **Business problem:** A customer's refund has not arrived after the expected window.
> **Demonstrates:** Multi-system lookup, status diagnosis, rule-based eligibility, human handoff for high-risk actions.

---

## Business Context

A customer contacts support reporting that a refund for order #XXXX has not arrived. The agent must:

1. Verify the order exists and belongs to the customer
2. Check refund initiation status in the payment system
3. Determine whether the refund window has elapsed
4. Diagnose the likely cause (bank delay, processing error, wrong account)
5. Provide an accurate status update or escalate if action is required

---

## Delivery Documents

| Document | Status |
|---|---|
| [Discovery](discovery.md) | Planned |
| [Workflow Map](workflow.md) | Planned |
| [Architecture](architecture.md) | Planned |
| [Risk Assessment](risks.md) | Planned |
| [Acceptance Criteria](acceptance.md) | Planned |
| [Evaluation Results](results.md) | Planned |

---

## Systems Integrated

| System | Role |
|---|---|
| CRM | Customer identity, order history |
| Payment API | Refund status, transaction log |
| Knowledge Base | Refund policy, processing timelines |

---

## Test It

```bash
docker compose up
```

Send:
```
My refund for order #10248 has not arrived. It has been 7 days.
```

Expected behavior:
- Agent looks up order and customer in CRM
- Agent checks refund status in payment system
- Agent compares elapsed time against policy
- Agent provides status update with expected resolution date
- If refund requires manual action → escalates to human agent
