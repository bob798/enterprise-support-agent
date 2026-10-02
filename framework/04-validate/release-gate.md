# Release Gate

> **Phase:** Validate
> **Purpose:** A single checklist that must pass before the system goes to production.
> **Rule:** No exceptions. If a criterion fails, fix it — do not adjust the threshold.

---

## Gate Checklist

### Quality

- [ ] Tool call accuracy ≥ 90% on golden dataset
- [ ] Factual groundedness ≥ 95% on human eval
- [ ] Handoff accuracy ≥ 92% on adversarial set

### Safety

- [ ] Zero unauthorized write actions in adversarial test
- [ ] Input guardrail tested with 10 harmful prompt variations
- [ ] PII does not appear in any logged response

### Performance

- [ ] P95 latency < 4 seconds under expected load
- [ ] Average cost per session < $0.05

### Operations

- [ ] `docker compose up` starts cleanly from a fresh clone
- [ ] All environment variables documented in `.env.example`
- [ ] Traces visible in observability dashboard
- [ ] Error alerting configured

### Documentation

- [ ] README run instructions accurate and tested
- [ ] Tool contracts up to date
- [ ] Known limitations documented

---

## Sign-off

| Role | Verified | Date |
|---|---|---|
| Engineer | | |
| QA / Evaluator | | |
| Delivery lead | | |

---

## Release Notes

**Version:**
**Date:**
**What changed:**
**Known limitations:**
