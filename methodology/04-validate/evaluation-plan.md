# Evaluation Plan

> **Phase:** Validate
> **Purpose:** Define how to prove the system is reliable before it handles real users.

---

## Golden Dataset

| Set | Size | Source | Purpose |
|---|---|---|---|
| Happy path | 30 cases | Real historical cases | Verify baseline capability |
| Edge cases | 15 cases | Crafted manually | Verify handling of unusual inputs |
| Adversarial | 20 cases | Red-team generated | Verify guardrails and safety |

**Total: 65 cases minimum before v1 release.**

---

## Evaluation Dimensions

### 1. Tool Call Accuracy

_Did the agent call the right tools with the right parameters?_

- Method: Compare actual tool calls against expected tool calls per test case
- Pass threshold: ≥ 90%

### 2. Factual Groundedness

_Is every claim in the response traceable to a tool output or knowledge document?_

- Method: Human evaluation of 50 randomly sampled responses
- Pass threshold: ≥ 95%

### 3. Handoff Accuracy

_Did the agent escalate when it should have, and not escalate when it shouldn't have?_

- Method: Run 20 adversarial cases designed to trigger/avoid handoff
- Pass threshold: ≥ 92%

### 4. Safety (Unauthorized Actions)

_Did the agent ever take a write action without required approval?_

- Method: Run 20 adversarial cases attempting to bypass approval
- Pass threshold: 100% (zero violations)

### 5. Latency

- Method: P95 across 100 sessions under realistic load
- Pass threshold: < 4 seconds

### 6. Cost

- Method: Average cost per session across 100 sessions
- Pass threshold: < $0.05

---

## Regression Tests

After any change to prompt, tools, or model:

- [ ] Re-run full golden dataset
- [ ] Compare results against previous baseline
- [ ] Flag any regression > 2% on any dimension

---

## Evaluation Results Template

| Dimension | Target | Result | Pass? |
|---|---|---|---|
| Tool call accuracy | ≥ 90% | | |
| Factual groundedness | ≥ 95% | | |
| Handoff accuracy | ≥ 92% | | |
| Unauthorized action rate | 0% | | |
| P95 latency | < 4s | | |
| Cost per session | < $0.05 | | |
