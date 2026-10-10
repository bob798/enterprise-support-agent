# Evaluation and safety — Refund Not Received

> Acceptance **plan**. Targets are not test results.

## Five release questions
| Check | Expected behavior | Evidence required |
|---|---|---|
| Correct status | Reply grounded in authorized API response | Golden cases + trace |
| Missing or ambiguous IDs | Ask for confirmation instead of guessing | Adversarial cases |
| Unclear / conflicting data | Escalate with known facts and missing evidence | Handoff review |
| Unauthorized write | No account/refund write tool exposed or invoked | Code inspection + safety tests |
| Privacy / permissions | Authenticate session, scope reads to merchant, mask sensitive data | Security tests |

## Primary risks
1. **False resolved:** refund status returned does not imply customer has received funds.
2. **Wrong merchant / order:** verify authorization and ambiguous identifiers.
3. **Stale or incomplete source data:** preserve timestamps, flag uncertainty, investigate or escalate.
4. **Funds operations:** never execute refund retry, balance adjustment or account write without separately authorized human-controlled workflow.
5. **Weak handoff:** include original issue, source results, errors, missing evidence and next action.

## Evidence status
The repository includes test source files in `tests/unit/`, `tests/safety/`, and `tests/integration/` (integration tests may require an API key). Their presence does not establish passing results. Publish tested commit, environment, run command and output before claiming quality.

The earlier detailed [acceptance.md](acceptance.md) contains a planned 160-case minimum; this **is not a completed 160-case test run**. Performance/accuracy/ROI claims remain unverified until measurements are published.
