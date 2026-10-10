# Discovery: Refund Not Received

> **Phase:** Discover
> **Date:** 2026-10-03
> **Problem area:** Payment technical support — merchant-reported refund delays
> **Source:** Interview with payment industry technical support practitioner

---

## Problem Statement

**Business problem:**
A merchant (B2B) submits a support ticket reporting that a refund they initiated has not been received by the buyer. The merchant contacts the payment company's technical support team to investigate.

**User persona:** B2B merchant — not the end consumer. The merchant is responsible for the buyer experience and needs a definitive answer to pass on.

**Frequency:** Medium — tens of tickets per week. A consistent, recurring request type, not a peak-driven spike.

**Why it matters:**
Refund status queries appear simple but require cross-system investigation. The result is communicated directly to merchants and affects their trust in the payment platform. A wrong answer is not just an inconvenience — it causes the merchant to stop pursuing a real problem.

---

## Current Workflow (Manual)

| Step | Actor | System | Notes |
|---|---|---|---|
| 1 | Support engineer | — | Request order number from merchant |
| 2 | Support engineer | Order / Transaction system | Look up refund status by order number |
| 3 | Support engineer | — | Classify result: clear / ambiguous / unresolvable |
| 4a (clear) | Support engineer | — | Inform merchant directly (e.g., refund failed, processing normally) |
| 4b (ambiguous) | Support engineer | Account / Balance system | Cross-system lookup — e.g., insufficient balance blocking refund |
| 4c (unresolvable) | Support engineer | Ticketing system | Escalate to senior / operations team |
| 5 | Support engineer | — | Provide final response to merchant |

**Key observation:** Steps 1–4a can be completed in ~5 minutes for clear cases. Ambiguous cases requiring cross-system investigation take 0.5 days as a unit of work — the investigation is non-trivial and highly dependent on individual expertise.

---

## Result Classification

| Status | Meaning | Next action |
|---|---|---|
| Refund in processing (within SLA) | Normal — no issue | Inform merchant, provide expected timeline |
| Refund already sent, buyer not received | Downstream issue (bank, account) | Investigate account / channel |
| Refund failed | System or account error | Identify cause, advise merchant |
| Insufficient account balance | Account issue blocking refund | Escalate — account operations require human approval |
| Ambiguous / multi-system issue | Requires deeper investigation | Cross-system lookup, potentially escalate |

---

## Systems Involved

| System | Role | Read / Write |
|---|---|---|
| Order / Transaction system | Look up order, refund initiation status | Read |
| Account / Balance system | Check account state, balance, constraints | Read |
| Ticketing system | Track and escalate cases | Read / Write |

**Note:** Any write operation affecting account state requires human approval. This is a hard boundary — not a policy preference.

---

## Cost & Impact

| Dimension | Current state | Target with AI |
|---|---|---|
| Simple case handling time | ~5 minutes | 0 (fully automated) |
| Complex case investigation time | ~0.5 days | ~1 hour |
| Human required for simple cases | Yes | No |
| Human required for account operations | Yes | Yes (unchanged) |

**Primary value driver:** Eliminating human involvement from simple, deterministic cases; dramatically compressing investigation time for complex cases.

---

## AI Suitability Score

| Dimension | Question | Score (1–3) |
|---|---|---|
| Information density | Requires querying multiple systems (order + account) | 3 |
| Repetition frequency | Tens of tickets per week, consistent pattern | 2 |
| Manual cost | Occupies skilled engineer time; complex cases take half a day | 3 |
| Process complexity | Multi-step with conditional branching | 3 |
| System integration | Requires reading from 2 systems | 3 |
| Business risk | Wrong answer causes merchant to abandon a real problem | 2 |
| Evaluability | Clear correct answer exists (ground truth in systems) | 3 |

**Total score: 19 / 21**

| Score | Recommendation |
|---|---|
| 16–21 | **Strong candidate — proceed to Design** |

**Industry benchmark:**
Ada reports 74% automated resolution rate on payment support tickets; Fini reports 98% accuracy on billing actions (3M+ monthly resolutions). This scenario's deterministic lookup pattern — query order status, classify result, route — aligns with the case types driving those numbers. The gap between simple (5 min) and complex (0.5 day) handling time further signals high automation headroom on the simple tier.

> Reference: [research/payment-support-ai-landscape.md](../../research/payment-support-ai-landscape.md)

---

## Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Agent returns incorrect refund status | **Critical** | Ground every status claim in tool output; never infer or guess |
| Agent communicates wrong result to merchant | **Critical** | Require confidence threshold before responding; ambiguous → human |
| Agent attempts account-related operations | **High** | Hard block: all account write operations require human approval |
| Merchant stops pursuing issue due to false "resolved" | **High** | Agent must distinguish "status retrieved" from "problem resolved" |

**Core principle:** In financial contexts, a confident wrong answer is worse than admitting uncertainty. The agent must escalate rather than guess.

**Industry validation:**
Fini (fintech-focused AI support platform) names this as their primary design constraint: *"a hallucinated refund is a direct financial loss."* Their RAGless architecture was built specifically to eliminate status inference — every claim must trace to a live API call, not a retrieved document. This validates the tool-first, grounding-required approach for this scenario.

> Reference: [research/payment-support-ai-landscape.md](../../research/payment-support-ai-landscape.md)

---

## Recommendation

**Decision: Proceed to Design**

**Rationale:**
- High suitability score (19/21)
- Clear system integration path (2 known APIs)
- Unambiguous human handoff boundary (account operations)
- Measurable success criteria (5 min → 0; 0.5 day → 1 hour)
- Risk is manageable with strict grounding and confidence gating

**Preconditions before Build:**
- [ ] API access confirmed for Order / Transaction system
- [ ] API access confirmed for Account / Balance system
- [ ] Escalation path defined (who receives handoff, in what format)
- [ ] Ground truth dataset sourced for evaluation (historical tickets)

---

## Open Questions

- [ ] What is the exact confidence threshold that triggers escalation vs. direct response?
- [ ] Does the agent respond directly to the merchant, or draft a response for the engineer to send?
- [ ] Are there additional systems (e.g., bank/channel layer) relevant for specific failure modes?
- [ ] What is the expected refund SLA — how does the agent determine if a delay is "normal"?
