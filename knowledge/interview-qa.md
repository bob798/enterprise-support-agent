# Enterprise AI Delivery — Interview Knowledge Base

> This document captures the reasoning behind every design decision in this project,
> structured as interview Q&A. The goal is not to memorize answers, but to be able
> to reconstruct them from first principles.
>
> **How to use:** Read the question. Close the document. Answer it. Check.

---

## Part 1: Design Decision Questions

### Q: Why did you use LangGraph instead of a simple LLM chain?

**Surface answer (avoid):** "LangGraph is recommended by Anthropic."

**Constraint-derived answer:**
This is a financial support workflow. Two constraints are non-negotiable:
1. Every state transition must be auditable — I need to know what the agent decided at each step
2. The workflow has conditional branches (failed → account lookup) and retry loops (ask for order ID up to 2 times)

A simple chain satisfies neither. A state machine makes every node transition explicit and serializable. LangGraph is the implementation of that topology. The Anthropic "Building Effective Agents" paper (2024) validates this — but the constraint drove the choice, not the paper.

**Follow-up: If LangGraph didn't exist, what would you use?**
Any framework that gives me: named nodes, serializable state, and conditional edges. Prefect, Temporal, or a hand-written state machine would all work. The architecture is the same; LangGraph just removes boilerplate.

---

### Q: Why is the routing logic in plain Python instead of an LLM decision?

**Constraint-derived answer:**
Routing is a write to the state field `next_action`. In a financial workflow, that field determines whether a merchant gets a direct reply or a human escalation. This decision must be:
- Deterministic (same input → same routing, every time)
- Version-controlled (routing changes show up in git diff, not in a prompt string)
- Testable (I can write a unit test that asserts `bank_error → escalate`)

LLM routing is probabilistic. Two identical inputs can produce different routing decisions across runs. That's incompatible with a financial audit requirement.

**The number:** arxiv 2603.01548 shows deterministic routing reduces LLM calls by 93% in tool-use pipelines, which also cuts cost. But the reason I chose it was auditability, not cost.

---

### Q: Why are responses generated from templates instead of letting Claude write them?

**Constraint-derived answer:**
The response generator's job is to communicate a financial status to a merchant. Every factual claim in that response — refund amount, expected arrival date, failure reason — comes from tool output, not from the model's knowledge.

If I let Claude generate the response, it might:
- Paraphrase ¥299 as "about ¥300"
- Invent an expected arrival date when none is available
- Say "your refund succeeded" when the status is "initiated"

The failure mode isn't hypothetical — Fini (a production support AI) explicitly names this: "a hallucinated refund is a direct financial loss." Risk R3 in this project (score 9/9) is exactly this: false "resolved" message causes merchant to stop following up.

Templates make hallucination architecturally impossible, not just probabilistically unlikely.

---

### Q: Why can't the agent trigger a refund retry? Isn't that useful?

**AI role boundary answer:**
This is a design decision, not a technical limitation. The tool layer contains zero write methods. This isn't enforced by a prompt ("you must not modify accounts") — it's enforced by the absence of the function.

**Why prompt guardrails aren't enough:** arxiv 2604.15579 shows symbolic (code-level) guardrails cannot be bypassed by adversarial prompts, unlike prompt-level guardrails. A prompt can be overridden by a clever input or a model update. An absent function cannot be called.

**The deeper reason (L4):** The AI role in this system is: query + communicate. Write operations on financial accounts require human accountability. This is where the EU AI Act's human oversight requirement (Art. 14) applies — systems affecting "important personal economic interests" need a human in the loop for consequential actions.

---

### Q: Why use Claude Haiku for intent classification instead of Sonnet?

**Answer:**
Intent classification is a structured extraction task: given a message, return `{intent, confidence, extracted_order_id}` as JSON. This doesn't require multi-step reasoning, nuanced judgment, or complex generation. Haiku is sufficient.

Sonnet is reserved for tasks that require more reasoning capacity — extended generation, complex ambiguity resolution. Currently, responses are template-based, so Sonnet isn't called at all in the current implementation.

**The cost implication:** Haiku is approximately 10× cheaper per token. At scale, every classification call being Haiku instead of Sonnet is a significant cost reduction with no quality loss on this task.

---

### Q: What's the highest risk in this system, and how did you mitigate it?

**Answer:**
Risk R3 (score 9 = 3 × 3): False "resolved" message causes merchant to stop pursuing a real problem.

What makes it the highest-scored risk isn't the probability — it's the invisibility. When the agent incorrectly says "your refund is processing," neither the agent nor the system knows it was wrong. The failure only surfaces when the buyer complains again, by which time SLA has been breached.

Mitigations:
1. The `succeeded` template explicitly prompts the merchant to confirm the buyer received funds
2. The `pending` template includes a re-contact deadline ("if still not received by X, resubmit")
3. The agent never uses the word "resolved" unless `refund_status = succeeded` AND merchant confirms receipt
4. There is a test specifically for this: `test_succeeded_reply_includes_confirmation_prompt`

---

### Q: How did you decide what the AI should and shouldn't do?

**Answer (L4 thinking):**
I started with a role table before any technical decisions:

| Decision type | Owner |
|---|---|
| What did the merchant ask? | AI (intent classifier) |
| What is the refund status? | Source system (tool) |
| What does this status mean? | Rule engine (deterministic) |
| What do we say? | Template (parameterized) |
| Should we escalate? | Rule engine (deterministic) |
| What action to take on account? | Human agent only |

This table is the answer to "what should AI do?" Everything that requires human accountability (write ops, ambiguous judgment) stays with humans. Everything that's pattern recognition or information relay goes to AI.

This isn't a soft preference — it's derived from the risk register. R4 (agent attempts write operations, score 8) and the EU AI Act Art. 14 human oversight requirement for systems affecting economic interests.

---

## Part 2: Thinking Framework Questions

### Q: Walk me through how you make architecture decisions.

**The 4-level framework:**

| Level | Question | Example |
|---|---|---|
| L1 (avoid) | "What does the paper recommend?" | "Anthropic says use state machines" |
| L2 | "What constraints must this design satisfy?" | "Financial audit requires deterministic transitions" |
| L3 | "What failures are unacceptable? Work backwards." | "Risk R3 score 9 → template responses required" |
| L4 | "What is the AI's role vs human's role?" | "AI queries and routes. Human decides and acts." |

The progression: L4 defines the boundary → L3 identifies what failures breach it → L2 derives the constraints → L2 selects the pattern that satisfies them → L1 validates with papers.

Papers are evidence, not motivation.

---

### Q: How do you know when to escalate to a human vs let the AI handle it?

**Constraint-based answer:**
Escalation criteria come from two sources:

1. **Failure reason opacity:** If the failure reason is one the agent has no tool to investigate (bank_error, order_expired), the agent lacks the capability to resolve it. Escalate.

2. **Write operation required:** If resolution requires modifying an account, triggering a retry, or overriding a policy decision — that's a human action. Escalate.

3. **Confidence below threshold:** If intent confidence < 0.70, the agent doesn't know what the merchant wants. Asking is always safer than assuming. Don't escalate — clarify first.

The rule is: **escalate when resolution exceeds tool capability, clarify when intent is unclear, respond directly only when both are certain.**

---

### Q: How do you think about AI accuracy requirements?

**Industry calibration:**
- Ada (Intercom): 74% resolution rate across all intents
- Fini: 98% resolution on payment support (scoped, structured domain)
- Zendesk baseline: ~60% on generic support

The gap between 74% and 98% is domain scoping. A generic support agent handles thousands of intent types — accuracy is limited by coverage. A payment-support agent handles 6 failure codes — accuracy is achievable because the domain is bounded.

The implication for requirements: **don't set accuracy targets before scoping the domain**. This project targets ≥ 90% intent classification accuracy because the domain is narrow and the mock data covers every branch.

---

## Part 3: What this project demonstrates

If asked "what does this project show about your abilities?":

1. **Enterprise delivery thinking:** Discover → Design → Build → Validate → Operate, with a worked example that shows each phase has specific outputs (not just vibes)

2. **Risk-first architecture:** Design decisions trace to specific risks with scores. The architecture isn't arbitrary — it's derived from what failures are unacceptable.

3. **AI role clarity:** I can articulate where AI agency ends and human judgment begins. This is the question enterprise clients ask, and it has a precise answer here.

4. **Testable safety properties:** Write-operation ban isn't a comment in the README — it's a test that fails if someone adds a write method. Confidence threshold isn't a config value — it's a test that pins it to 0.70 and requires an eval run if it changes.

---

*Last updated: 2026-10-04*
*Companion files: `agent/DESIGN.md` (engineering rationale), `examples/refund-not-received/risks.md` (risk register)*
