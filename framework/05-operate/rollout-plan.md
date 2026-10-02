# Rollout Plan

> **Phase:** Operate
> **Purpose:** Define how the system reaches users safely, with a clear path to expand or roll back.

---

## Rollout Stages

### Stage 1: Internal (Week 1–2)

- Audience: Internal team only
- Traffic: 100% of internal test sessions
- Goal: Catch issues before real users see them
- Exit criteria: No P0 bugs, latency within target

### Stage 2: Limited Pilot (Week 3–4)

- Audience: _[define user segment]_
- Traffic: _[% of eligible sessions]_
- Goal: Validate quality on real inputs
- Exit criteria: Quality metrics within target, user satisfaction > _[threshold]_

### Stage 3: Full Rollout

- Audience: All eligible users
- Traffic: 100%
- Goal: Full production operation
- Exit criteria: Stable for 5 business days with no P0/P1 incidents

---

## Rollback Criteria

Roll back immediately if:

- [ ] Unauthorized action detected in production
- [ ] Latency P95 > 8 seconds for > 10 minutes
- [ ] Error rate > 5% for > 5 minutes
- [ ] User-reported factual error confirmed

**Rollback procedure:**

1. Set traffic to 0% for AI path
2. Route all sessions to human agents
3. Page on-call engineer
4. Investigate before any re-release

---

## On-Call Runbook

| Symptom | Check | Action |
|---|---|---|
| Slow responses | Trace dashboard | Check tool latency, LLM API status |
| Wrong answers | Eval dashboard | Check if tool returned bad data |
| High cost spike | Cost dashboard | Check for prompt injection or loop |
| Escalation storm | Handoff rate | Check if confidence calibration drifted |
