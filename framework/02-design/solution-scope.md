# Solution Scope

> **Phase:** Design
> **Purpose:** Define what the system will and will not do before any code is written.

---

## System Name

**Working name:**

---

## In Scope

What the system handles in v1:

- [ ]
- [ ]
- [ ]

## Out of Scope (v1)

What is explicitly excluded:

- [ ]
- [ ]

---

## Responsibility Boundary

| Responsibility | Owner |
|---|---|
| Understanding user intent | LLM |
| Retrieving factual data | Tool / API |
| Applying business rules | Rules engine / Policy layer |
| Making final decisions | Human (for high-risk) |
| Taking irreversible actions | Human approval required |

---

## Agent Architecture

```
User input
  → Intent classification
    → [Tool calls: CRM / Payment / Knowledge]
      → Response synthesis
        → [Guardrail check]
          → Response / Handoff decision
```

---

## Handoff Criteria

The agent escalates to a human when:

- [ ] Confidence below threshold: _[define]_
- [ ] Action type: _[list irreversible actions]_
- [ ] Detected intent: _[list escalation intents]_
- [ ] Error condition: _[list failure modes]_

---

## Non-Functional Requirements

| Requirement | Target |
|---|---|
| P95 latency | |
| Cost per session | |
| Availability | |
| Data retention | |
