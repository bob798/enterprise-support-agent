# Payment Support AI — Industry Landscape & Best Practices

> **Last updated:** 2026-10-03
> **Scope:** AI platforms and architectures for automating refund, billing, and payment support workflows
> **Purpose:** Inform design decisions for the enterprise-support-agent examples

---

## Market Overview

Enterprise AI support automation for payments has matured into a distinct product category. Key players target different segments:

| Platform | Founded | Focus | Key customers |
|---|---|---|---|
| **Ada** | 2016, Toronto | Horizontal customer service AI | Meta, Shopify, Square, Verizon |
| **Fini** | — | Fintech / payments-first AI support | Fintech enterprises |
| **Zendesk AI** | — | Ticketing + AI (via Ultimate.ai, acq. 2024) | Broad enterprise |
| **Decagon** | 2023, SF | Enterprise support automation | Eventbrite, Bilt Rewards, Substack |

**Funding signals:**
- Ada: raised > $190M
- Decagon: backed by a16z, Accel, Bain Capital Ventures

---

## Performance Benchmarks

| Platform | Metric | Value | Notes |
|---|---|---|---|
| Ada | Automated resolution rate | **74%** | Average across customer base |
| Fini | Billing action accuracy | **98%** | Zero hallucinations on billing |
| Fini | Monthly resolutions processed | **3M+** | As of 2026 |
| Zendesk AI | Resolution rate (deterministic tickets) | **60–70%** | Billing workflows sit below this |
| Fini / structured approach | Resolution rate uplift vs. RAG | **85–90%** vs 50–60% | Same underlying model, different architecture |

**Industry pattern:** The 50–60% resolution ceiling is consistent across RAG-based approaches. Structured reasoning architectures break through to 85–90%.

---

## Architecture Patterns

### Pattern 1: RAG-based (industry default, limited ceiling)

Most platforms start here. Retrieves relevant documents at query time, passes to LLM for synthesis.

**Weakness in payment contexts:** Document retrieval is probabilistic. For status queries ("is this refund processed?"), the ground truth is in the live system, not a document. RAG cannot retrieve a fact that isn't in the knowledge base — it will infer, which means hallucinate.

---

### Pattern 2: RAGless / Structured Reasoning (Fini's approach)

**Core insight (Fini):** Replace fuzzy document retrieval with a structured knowledge tree. The agent traverses the tree like a senior support agent following a decision tree, rather than doing probabilistic search.

```
Traditional RAG:
  Query → Vector search → Retrieved docs → LLM generates answer
                                ↑
                          hallucination risk here

RAGless (Fini):
  Query → Intent classification → Knowledge Tree traversal → Live API call → Grounded answer
                                                                    ↑
                                               fact comes from system, not document
```

**Knowledge Atlas (Fini):**
- Knowledge Tree: navigable hierarchy of folders + articles with semantic descriptions
- Agent walks the tree top-down, like a human reading a decision flowchart
- Self-updating loop: captures resolutions, detects policy conflicts, keeps knowledge current
- Reported: reduces manual documentation work by 90%

**Why this matters for this repository:**
The refund-not-received scenario is a decision tree, not a search problem. The correct answer is always retrievable from a live API (order status, account balance). The agent should call tools, not retrieve documents, for factual claims.

---

### Pattern 3: Tool-first Workflow (this repository's approach)

```
User message
  → Intent: refund status inquiry
    → Tool: query_order_status(order_id)
      → Tool: query_account_balance(account_id)  [if needed]
        → Classify result: clear / ambiguous / unresolvable
          → Route: respond / investigate further / escalate
```

Every factual claim traces to a tool output. No inference on financial status.

This aligns with Fini's core principle and is validated by their production accuracy numbers.

---

## Key Design Decisions (industry-validated)

### 1. Tool-first, not RAG-first for status queries

For queries where ground truth exists in a live system (order status, account balance, refund state), always call the API. Never retrieve a document and infer.

**Evidence:** Fini explicitly states: *"a hallucinated refund is a direct financial loss."* RAGless was built to eliminate this.

### 2. Hard boundary on write operations

All platforms surveyed maintain a hard human-approval gate for account modifications, refund initiation, and any financial write operation.

**Evidence:** Cross-platform pattern — not a conservative design choice but an industry standard in regulated domains.

### 3. Escalation with context, not just a handoff

When escalating to a human, pass a decision summary: what was checked, what was found, why it couldn't be resolved automatically.

**Evidence:** [ValPay escalation guidelines](https://partners.valpay.com/en/articles/15565615-getting-help-psp-references-escalation-details-and-voids-vs-refunds) — escalation should include PSP reference, error codes, and steps already taken.

### 4. Confidence gate before responding

Ada, Fini, and Decagon all implement a confidence / routing threshold before surfacing an answer. Below threshold → escalate. Never guess in financial contexts.

---

## B2B vs B2C Gap

**Critical observation:** All major platforms target B2C (consumer contacting payment company).

The B2B scenario (merchant contacting payment company) is underserved:

| Dimension | B2C | B2B (this repo's focus) |
|---|---|---|
| Caller sophistication | End consumer | Technical merchant team |
| Answer precision required | General guidance | Exact status, traceable |
| Error consequence | User frustration | Merchant stops pursuing real issue |
| Query complexity | Simple (my order) | Multi-system (their buyer's order) |
| Permission model | Self-service | Role-based, account-level |

This gap is the differentiation opportunity for this repository.

---

## Existing Open-Source References

Fini itself is **not open source** (commercial SaaS). The closest open-source alternatives are focused on financial analysis rather than support:

| Project | Focus | Relevant? |
|---|---|---|
| [FinRobot](https://github.com/ai4finance-foundation/finrobot) | Financial decision intelligence, quant models | Partially — agent architecture patterns |
| [FinWorld](https://github.com/TradeMaster-NTU/FinWorld) | End-to-end financial AI research platform | Partially — evaluation framework |

Neither covers enterprise support automation. This repository fills that gap with a runnable, evaluated example.

---

## Sources

- [Beyond Chatbots: 5 Next-Gen Use Cases for AI Agents in Customer Support (Composio, 2026)](https://composio.dev/blog/ai-agents-customer-support-use-cases)
- [RAGless: The Architecture Behind Accuracy-first AI for Customer Support (Fini)](https://www.usefini.com/blog/what-is-ragless)
- [The Knowledge Atlas: Structured Reasoning for Enterprise AI Support (Fini)](https://www.usefini.com/resource-library/the-knowledge-atlas-structured-reasoning-and-autonomous-management-for-enterprise-ai-support)
- [AI for Refund Status Customer Service (Lorikeet)](https://www.lorikeetcx.ai/articles/ai-for-refund-status-customer-service)
- [Refund Operations Runbook (PaymentBrief)](https://paymentbrief.com/articles/refund-operations-runbook/)
- [Troubleshooting Checklist for B2B Payment Failures (Bectran)](https://www.bectran.com/post/troubleshooting-checklist-b2b-payment-failures)
- [Getting Help: PSP References, Escalation Details, and Voids vs Refunds (ValPay)](https://partners.valpay.com/en/articles/15565615-getting-help-psp-references-escalation-details-and-voids-vs-refunds)
- [FinRobot: Open-Source AI Agent for Financial Applications](https://github.com/ai4finance-foundation/finrobot)
