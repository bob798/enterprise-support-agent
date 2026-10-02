# Acceptance Criteria

> **Phase:** Design
> **Purpose:** Define what "done" means before building starts. These criteria gate the v1 release.

---

## Functional Criteria

| # | Criterion | How to verify | Pass threshold |
|---|---|---|---|
| F1 | Agent correctly identifies the issue type | Golden dataset, 50 cases | ≥ 90% |
| F2 | Agent retrieves correct data from CRM | Tool call audit log | ≥ 95% |
| F3 | Agent response is factually grounded | Human eval, 50 cases | ≥ 95% |
| F4 | Agent escalates correctly when uncertain | Adversarial test set, 20 cases | ≥ 92% |
| F5 | Agent never takes unauthorized action | Adversarial test set, 20 cases | 100% |

---

## Non-Functional Criteria

| # | Criterion | Measurement | Pass threshold |
|---|---|---|---|
| NF1 | End-to-end latency | P95 across 100 sessions | < 4 seconds |
| NF2 | Cost per session | Average over 100 sessions | < $0.05 |
| NF3 | System availability | Uptime over 7-day test | ≥ 99% |

---

## Out-of-Scope for v1

The following are not required to pass acceptance:

- Multi-language support
- Mobile UI
- Real-time streaming responses
- _[add more]_

---

## Release Gate Sign-off

| Role | Name | Signed off | Date |
|---|---|---|---|
| Engineer | | | |
| QA | | | |
| Product / Delivery | | | |
