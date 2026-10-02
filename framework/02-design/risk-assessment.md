# Risk Assessment

> **Phase:** Design
> **Purpose:** Identify, score, and mitigate risks before implementation begins.

---

## Risk Register

| # | Risk | Likelihood | Impact | Score | Mitigation |
|---|---|---|---|---|---|
| 1 | Agent returns incorrect factual data | Med | High | 6 | Ground all responses in tool output; cite source |
| 2 | Agent takes unauthorized action | Low | Critical | 8 | Require human approval for write operations |
| 3 | Agent hallucinates policy | Med | High | 6 | RAG from authoritative policy docs only |
| 4 | Sensitive data exposed in response | Low | High | 4 | PII masking on output layer |
| 5 | System latency causes user drop-off | Med | Med | 4 | Streaming responses; P95 < 4s target |

_Likelihood: Low=1, Med=2, High=3. Impact: Low=1, Med=2, High=3, Critical=4. Score = Likelihood × Impact._

---

## Guardrail Design

| Guardrail | Type | Trigger condition | Action |
|---|---|---|---|
| Harmful content filter | Input | User message contains [pattern] | Reject + log |
| Unauthorized action gate | Output | Tool requires write permission | Require approval |
| Confidence threshold | Output | Confidence < 0.7 | Escalate to human |
| PII masker | Output | Response contains email/phone | Mask before sending |

---

## Human-in-the-Loop Triggers

Actions that always require human approval before execution:

- [ ] Initiating a refund > $[threshold]
- [ ] Modifying account status
- [ ] Sending external communications
- [ ] _[add more]_

---

## Residual Risks (accepted)

| Risk | Why accepted | Owner |
|---|---|---|
| | | |
