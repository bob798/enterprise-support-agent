# Tool Contract

> **Phase:** Design
> **Purpose:** Define every tool the agent can call — name, inputs, outputs, errors, and permissions.
> **Instructions:** One section per tool. This document is the contract between the agent and the integration layer.

---

## Tool: `[tool_name]`

**Description:** _What this tool does in one sentence._

**When to call:** _Conditions under which the agent should invoke this tool._

**Inputs:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| | string | Yes | |

**Outputs:**

| Field | Type | Description |
|---|---|---|
| | string | |

**Error cases:**

| Error code | Meaning | Agent behavior |
|---|---|---|
| NOT_FOUND | Resource does not exist | Inform user, do not retry |
| UNAUTHORIZED | Caller lacks permission | Escalate to human |
| TIMEOUT | System unavailable | Retry once, then escalate |

**Permission level:** `read` / `write` / `admin`

**Requires human approval before execution:** Yes / No

---

## Tool: `[tool_name]`

_(Copy section above for each additional tool)_

---

## Tool Registry Summary

| Tool | Permission | Human approval | System |
|---|---|---|---|
| | read | No | |
