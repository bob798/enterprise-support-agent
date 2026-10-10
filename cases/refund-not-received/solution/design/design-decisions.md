# Agent Design Document

> **Scope:** `agent/` package — LangGraph state machine for the refund-not-received workflow
> **Date:** 2026-10-04
> **Audience:** Engineers inheriting or extending this system

---

## 1. AI Role Declaration (Why this document exists)

Before any technical decision, this system requires an explicit answer to:

> **What does the AI decide? What does a human decide?**

| Decision type | Owner | Rationale |
|---|---|---|
| "What did the merchant ask?" | AI (intent classifier) | Pattern recognition; low financial risk |
| "What is the refund status?" | Source system (via tool) | Financial data must be authoritative, not inferred |
| "What does this status mean?" | Rule engine (router) | Must be deterministic and auditable |
| "What do we say to the merchant?" | Template (parameterized) | Financial accuracy cannot tolerate free-form generation |
| "Should we escalate?" | Rule engine (router) | Routing logic must be version-controlled and reviewable |
| "What action to take on the account?" | Human agent only | Write operations on financial accounts require human accountability |

**This is not a technical preference. It is a compliance requirement.**

EU AI Act (2024) Article 14 requires human oversight mechanisms for AI systems affecting "important personal economic interests." This role boundary is where that mechanism lives. Every design decision below is derived from this table.

---

## 2. Non-Negotiable Constraints

These constraints are fixed by the domain, not by technology preference. Architecture must satisfy all of them.

| # | Constraint | Source | Consequence if violated |
|---|---|---|---|
| C1 | Financial status data must come from source systems, never from LLM inference | Domain (payment compliance) | Wrong status → merchant tells buyer money is coming → trust failure |
| C2 | Every state transition must be logged and auditable | Regulatory (financial audit trail) | Cannot reconstruct what the agent decided or why |
| C3 | Write operations on accounts are categorically prohibited | Risk register R4, AI role boundary | Agent triggers unintended financial side effect |
| C4 | When confidence is below threshold, ask — do not guess | Risk register R7 | Misrouted message causes wrong outcome with false confidence |
| C5 | Escalation must carry full context | Risk register R6 | Human agent re-queries from scratch — defeats purpose of automation |
| C6 | Merchant identity must come from authenticated session, never from message body | Risk register R10 | Cross-merchant data exposure |

---

## 3. Risk → Design Traceability

Each major architectural decision traces directly to a risk in `risks.md`. Papers and patterns are validation, not motivation.

| Risk | Score | Design response | Where in code |
|---|---|---|---|
| R1 — Wrong status returned | 8 | Tool wraps API; result passed through unchanged to template | `tools/refund_status.py` |
| R2 — Wrong result communicated | 8 | Template responses with required-field validation; no LLM generation of financial claims | `nodes/responder.py`, `prompts/response.py` |
| R3 — False "resolved" (highest risk, score 9) | 9 | `succeeded` template includes confirmation prompt; `pending` includes re-contact deadline | `prompts/response.py` lines 15–30 |
| R4 — Agent attempts write operations | 8 | Tool layer has zero write methods — architectural prohibition, not prompt prohibition | `tools/` directory |
| R5 — Wrong order ID extracted | 6 | Collector node re-confirms; max 2 retries before escalation | `nodes/collector.py` |
| R6 — Incomplete escalation payload | 4 | Escalator validates required fields before sending | `nodes/escalator.py` |
| R7 — Overconfident misrouting | 6 | `CONFIDENCE_THRESHOLD = 0.70`; below threshold → ask, never assume | `nodes/intent.py:16` |
| R8 — Tool timeout | 4 | Retry once; on failure escalate with `failure_reason_code = "api_timeout"` | `tools/refund_status.py` |
| R9 — PII in IM response | 4 | Templates mask account/card fields before send | `prompts/response.py` |
| R10 — Webhook spoofing | 8 | `merchant_id` from authenticated session binding; all tool queries scoped to it | `api.py`, `AgentState` |

---

## 4. Design Decisions

### D1 — State machine topology (LangGraph)

**Constraint satisfied:** C2 (auditable state transitions)

**Derivation:** A financial support workflow has fixed subtasks in a known sequence: classify → collect → query → route → respond/escalate. Free-form LLM agent loops cannot guarantee every step is logged, retried predictably, or interrupted for human takeover. A state machine makes every node transition explicit and serializable.

**Why not a simple chain?** Chains have no conditional branching or cycle support. This workflow requires both: retry loops for order ID collection, and branching based on failure reason codes.

**External validation:** Anthropic "Building Effective Agents" (2024) — *"For workflows with fixed subtasks, state machines are more reliable than free-form agent loops."* LangGraph is Anthropic's reference implementation of this pattern.

---

### D2 — Deterministic routing (no LLM in routing decisions)

**Constraint satisfied:** C2 (auditable), AI role boundary (AI does not decide "should we escalate")

**Derivation:** Routing in `router.py` is pure Python: `if failure_reason in DIRECT_REPLY_REASONS`. This means routing decisions are version-controlled, unit-testable, and reviewable by non-engineers. If the routing logic changes, it shows up in a git diff — not in a prompt string.

**Why not LLM routing?** LLM routing is probabilistic. Two identical inputs may produce different routing decisions across runs. In a financial audit, "the model decided to escalate" is not an acceptable explanation.

**External validation:** arxiv 2603.01548 — deterministic routing reduces LLM calls by 93% in tool-use pipelines and makes failure modes predictable.

---

### D3 — Template responses (no LLM generation of financial content)

**Constraints satisfied:** C1 (no LLM inference on financial data), R2, R3

**Derivation:** The response generator in `responder.py` fills parameterized templates from `AgentState` fields. It does not call Claude to "write a response." This means:
- Every financial figure in the response (`refund_amount`, `expected_arrival`) comes directly from the tool output
- A code reviewer can verify the response text by reading the template
- Hallucination of financial content is architecturally impossible, not probabilistically unlikely

**The failure mode this prevents:** LLM generates "your refund of ¥1,200 will arrive by Friday" when the actual amount is ¥120 and no arrival date is available.

**External validation:** This is the core principle behind Fini's architecture (*"a hallucinated refund is a direct financial loss"*) and the grounding requirement in `acceptance.md` eval dimension E3.

---

### D4 — Write operations banned at the architectural level

**Constraints satisfied:** C3 (no write ops), R4

**Derivation:** The `tools/` directory contains no write methods. This is not enforced by a prompt ("you must not modify accounts") — it is enforced by the absence of the capability. A prompt guardrail can be overridden by a sufficiently clever input or a model update. An absent function cannot be called.

**External validation:** arxiv 2604.15579 — *"symbolic guardrails (code-level restrictions) cannot be bypassed by adversarial prompts, unlike prompt-level guardrails."* The paper distinguishes these as categorically different security properties.

---

### D5 — Model routing: Haiku for classification, Sonnet for generation

**Constraint satisfied:** (no hard constraint — cost/quality optimization)

**Derivation:** Intent classification is a structured JSON extraction task: given a message, return `{intent, confidence, extracted_order_id}`. This does not require reasoning about context, nuance, or multi-step logic. Haiku is sufficient and approximately 10× cheaper per token than Sonnet.

Response generation is currently template-based (see D3), so Sonnet is not currently called for response text. If the system is extended to handle more complex scenarios requiring natural language generation, Sonnet is the appropriate model because it handles ambiguous merchant language better.

**External validation:** Anthropic model routing guide — Haiku for extraction/classification tasks, Sonnet for generation/reasoning tasks.

---

### D6 — AgentState as single source of truth

**Constraint satisfied:** C2 (auditability — full state is serializable at any point)

**Derivation:** Every node reads from and writes to `AgentState`. No node holds local state that isn't reflected in the shared state dict. This means:
- Any node can be re-run from a checkpoint without side effects
- The full conversation state can be inspected at any point for debugging or audit
- Adding a new node only requires defining which state fields it reads and writes

**Why TypedDict?** LangGraph requires it for type inference in conditional edge functions. The explicit field types also serve as documentation of what each node can produce.

**External validation:** Redux/Flux unidirectional data flow pattern (2015) — single shared state store, each component writes only its own slice. Applied to agent systems by LangGraph's design.

---

### D7 — Mock/Real connector interface

**Constraint satisfied:** (deployment flexibility — not a safety constraint)

**Derivation:** `connectors/mock/` and `connectors/real/` implement the same function signatures. The `CONNECTOR_MODE` environment variable selects which to load at import time. This means:
- Local development and CI run with zero external dependencies
- Production deployment swaps one environment variable
- The agent code has no conditionals for "are we in mock mode?"

**External validation:** SOLID Dependency Inversion Principle — depend on abstractions, not concretions. 12-Factor App Factor III — *"backing services are attached resources, swapped via config."*

---

## 5. What this system explicitly does not do

These are design decisions by omission. They define the system boundary.

| Capability | Excluded | Reason |
|---|---|---|
| Trigger refund retry | No | Write operation — R4, AI role boundary |
| Adjust refund amount | No | Write operation — R4, AI role boundary |
| Answer questions about other topics | No | Out of scope — C4, clarification required |
| Make judgment calls on ambiguous failure reasons | No | Unknown → escalate (router.py fallback) |
| Remember previous conversations | No | Stateless per session — no session persistence in v1 |
| Generate free-form explanations of payment policy | No | Policy interpretation requires human accountability |

---

## 6. Extension points

When extending this system, preserve these invariants:

1. **Any new tool must be read-only.** If a write capability is ever required, it must go through a separate human-approval workflow, not through this agent.
2. **Any new routing decision must be expressible as a Python conditional.** If it requires LLM judgment, it belongs in a separate classification node with its own confidence threshold and escalation path.
3. **Any new response template must be parameterized from AgentState fields only.** No free-form generation from financial data.
4. **Any change to the confidence threshold must have a corresponding eval run.** `CONFIDENCE_THRESHOLD = 0.70` is not arbitrary — it was calibrated against the golden dataset in `evals/`.

---

*References: Anthropic "Building Effective Agents" (2024) · arxiv 2603.01548 · arxiv 2604.15579 · Fini architecture blog · EU AI Act Art.14 (2024) · Stuart Russell "Human Compatible" (2019) · George Fairbanks "Just Enough Software Architecture" (2010) · 12-Factor App (Wiggins, 2011)*
