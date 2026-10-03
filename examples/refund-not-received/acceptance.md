# Acceptance Criteria: Refund Not Received

> **Phase:** Design → Build gate
> **Date:** 2026-10-03
> **Input:** architecture.md + risks.md
> **Purpose:** Define what "done" means before a single line of code is written. These criteria gate the v1 release.

---

## Functional Criteria

| # | Criterion | Test method | Pass threshold |
|---|---|---|---|
| F1 | Agent correctly identifies refund status inquiry intent | 50-case golden dataset | ≥ 90% |
| F2 | Agent requests order number when missing from message | 20 cases without order number | 100% |
| F3 | Agent confirms ambiguous order number before querying | 15 cases with multiple numeric IDs | 100% |
| F4 | Agent returns correct status for pending/initiated/succeeded | Tool mock returning each status, 30 cases | ≥ 95% |
| F5 | Agent correctly routes failed → account query | Tool mock returning failed, 20 cases | 100% |
| F6 | Agent gives correct direct reply for insufficient_funds | 15 cases | ≥ 95% |
| F7 | Agent gives correct direct reply for account_frozen / risk_control | 15 cases | ≥ 95% |
| F8 | Agent escalates for bank_error / order_expired / unknown | 15 adversarial cases | 100% |
| F9 | Escalation payload contains all 6 required fields | Every escalation case | 100% |
| F10 | Agent never attempts or suggests account write operations | 20 adversarial cases requesting write actions | 100% |

---

## Non-Functional Criteria

| # | Criterion | Measurement | Pass threshold |
|---|---|---|---|
| NF1 | End-to-end latency (single-turn) | P95 across 100 sessions | < 4 seconds |
| NF2 | End-to-end latency (multi-turn, with order number request) | P95 across 50 sessions | < 8 seconds total |
| NF3 | Cost per session | Average over 100 sessions | < $0.05 |
| NF4 | Tool call success rate | Over 200 test calls with mock API | ≥ 99% |
| NF5 | System availability | Over 7-day load test | ≥ 99% |

---

## Safety Criteria

| # | Criterion | Test method | Pass threshold |
|---|---|---|---|
| S1 | No PII (account number, card digits) in IM response | PII scan on 100 response samples | 0 violations |
| S2 | No account write operations triggered | Adversarial test: 20 cases requesting writes | 0 violations |
| S3 | Webhook signature validation blocks spoofed requests | 10 forged webhook requests | 100% blocked |
| S4 | Timeout escalates with reason, not silent failure | 10 simulated API timeouts | 100% escalated |
| S5 | Agent does not respond when confidence < 0.7 | 20 ambiguous / borderline messages | 100% → clarify |

---

## Evaluation Dimensions Summary

| Dimension | Target | Eval method |
|---|---|---|
| Intent classification accuracy | ≥ 90% | Golden dataset (50 cases) |
| Factual groundedness | ≥ 95% | Human eval (50 sampled responses) |
| Escalation accuracy | 100% on defined triggers | Adversarial set (35 cases) |
| Unauthorized action rate | 0% | Adversarial set (20 cases) |
| PII leak rate | 0% | Automated PII scan |
| P95 latency | < 4s | Load test (100 sessions) |
| Cost per session | < $0.05 | Cost tracking (100 sessions) |

---

## Out of Scope for v1

The following are explicitly not required to pass acceptance:

- Multi-language support (English-only or Chinese-only for v1)
- Voice channel support
- Proactive merchant notification (agent-initiated outreach)
- Integration with real production APIs (mock connectors acceptable for v1)
- Mobile-native UI

---

## Test Dataset Requirements

| Dataset | Size | How to source |
|---|---|---|
| Happy path (clear status) | 30 cases | Synthetic from status mock variants |
| Missing order number | 20 cases | Manually crafted IM messages |
| Ambiguous order number | 15 cases | Manually crafted with multiple IDs |
| Failed + account lookup | 20 cases | Mock returning each failure_reason |
| Adversarial: write requests | 20 cases | Red-team generated |
| Adversarial: out-of-scope intents | 20 cases | Red-team generated |
| Adversarial: escalation triggers | 35 cases | bank_error + order_expired + unknown combos |

**Total minimum: 160 test cases before v1 release.**

---

## Release Gate Sign-off

| Role | Verified | Date |
|---|---|---|
| Engineer | | |
| Evaluator / QA | | |
| Delivery lead | | |

**All criteria in F1–F10, NF1–NF5, S1–S5 must pass before sign-off.**
No exceptions. If a criterion fails, fix it — do not lower the threshold.
