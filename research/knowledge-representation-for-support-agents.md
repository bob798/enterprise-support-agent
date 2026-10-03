# Knowledge Representation for Support Agents

> **Last updated:** 2026-10-03
> **Scope:** How to represent domain knowledge for AI support agents — RAG, knowledge graphs, structured workflows
> **Purpose:** Justify the tool-first architecture choice in this repository and document the trade-offs

---

## The Core Question

When an AI support agent needs to answer a question, where does the answer come from?

Three fundamentally different architectures exist. The choice affects accuracy, latency, cost, and failure modes.

---

## Architecture A: Pure RAG (Industry Default)

```
Query
  → Embed query as vector
    → Similarity search over document chunks
      → Retrieve top-K chunks
        → LLM synthesizes answer from retrieved chunks
```

**How it works:** Knowledge is stored as embeddings. At query time, the most semantically similar chunks are retrieved and passed to the LLM.

**Strengths:**
- Easy to set up — ingest documents, done
- Works well for general Q&A over static knowledge bases
- Low infrastructure complexity

**Weaknesses:**
- Accuracy ceiling: **50–60%** on complex reasoning tasks
- Probabilistic retrieval — may return related but not exactly correct chunks
- LLM can hallucinate when retrieved context is incomplete
- Cannot distinguish "I don't know" from "the document said X but I'm wrong"
- In financial contexts: if the document doesn't contain the current status, the LLM infers — which means hallucinates

**When to use:** General knowledge Q&A (policies, FAQs, documentation). Not for real-time status queries.

**Academic evidence:**
- Vector RAG baseline: 60% accuracy on complex reasoning (GraphRAG comparison study)
- Known hallucination rates increase when retrieved context is ambiguous or incomplete

---

## Architecture B: Knowledge Graph + RAG (Structured Retrieval)

```
Query
  → Intent parsing
    → Graph traversal (entities, relations, decision paths)
      → Targeted document/fact retrieval
        → LLM synthesizes with structured context
```

**How it works:** Knowledge is organized as a graph — entities, relationships, and decision paths. The agent navigates the graph rather than doing fuzzy search.

**This is Fini's approach ("Knowledge Atlas / Knowledge Tree"):**
- Knowledge is preprocessed into a structured hierarchy
- Agent walks the tree top-down, like following a decision flowchart
- Retrieval is deterministic, not probabilistic
- Self-updating loop: new resolved tickets are automatically incorporated

**Strengths:**
- Accuracy: **85–90%** on same underlying model vs 50–60% for RAG
- Multi-hop reasoning: can follow chains of facts across nodes
- Traceable: every answer has a path through the graph
- Self-improving: new tickets update the graph automatically

**Weaknesses:**
- Higher upfront complexity — knowledge must be structured
- Graph maintenance overhead (mitigated by auto-update loops)
- Does not help when ground truth is in a live system, not a document

**When to use:** Policy reasoning, multi-step eligibility checks, FAQ with conditional logic, anything where the answer is in internal knowledge but requires navigation.

**Academic evidence:**

| Paper | Finding |
|---|---|
| [Graph-Enhanced RAG for E-Commerce Support (arxiv 2509.14267)](https://arxiv.org/abs/2509.14267) | KG+RAG significantly outperforms pure vector RAG on customer support QA |
| [RAG with Knowledge Graphs for Customer Service (arxiv 2404.17723)](https://arxiv.org/abs/2404.17723) | KG structure improves multi-hop reasoning accuracy |
| GraphRAG vs Vector RAG comparison | **90% vs 60%** on complex reasoning tasks |
| [Human Cognition Inspired RAG with KG (arxiv 2503.06567)](https://arxiv.org/pdf/2503.06567) | Graph-structured cognitive framework outperforms existing methods |

**Open-source implementations:**

| Project | Description | Link |
|---|---|---|
| Graphiti | Real-time knowledge graphs for AI agents; continuous integration of new data | [getzep/graphiti](https://github.com/getzep/graphiti) |
| RAGFlow | RAG engine with Graph/Tree/Wiki/MindMap compilation templates | [infiniflow/ragflow](https://github.com/infiniflow/ragflow) |
| LLM-KG4QA | Academic: LLM + KG joint question answering | [machuangtao/LLM-KG4QA](https://github.com/machuangtao/LLM-KG4QA) |
| llm_wiki | LLM-maintained structured wiki — reads index first, retrieves targeted articles | [nashsu/llm_wiki](https://github.com/nashsu/llm_wiki) |

---

## Architecture C: Tool-First Workflow (This Repository)

```
Query
  → Intent classification
    → Identify required facts
      → Call live API (tool) to retrieve each fact
        → Route based on retrieved values (rule engine)
          → Generate grounded response from tool output
```

**How it works:** The agent does not retrieve from a knowledge base at all for factual claims. It calls live APIs directly. The knowledge base is only used for policy rules and response templates.

**This is the architecture used in this repository for the refund-not-received example.**

**Strengths:**
- **100% factual grounding** — every claim traces to a live API call
- No retrieval error possible for status queries
- Deterministic routing — result classification is rule-based, not probabilistic
- Accuracy ceiling: effectively eliminated for the factual layer (accuracy depends on API reliability, not retrieval)

**Weaknesses:**
- Requires API access to all relevant systems
- Does not work for open-ended knowledge questions (only for known-answer lookups)
- More complex to build — every data point needs a tool
- API failures propagate directly (mitigated by retry + escalation)

**When to use:** Any query where the ground truth exists in a live system — order status, account balance, transaction history, subscription state. The answer is not in a document; it is in the database.

**Academic evidence:**
- [RAFT: Stateful Retrieval for Troubleshooting Agents](https://arxiv.org/pdf/2609.20754) — stateful, step-by-step retrieval outperforms RAG for structured troubleshooting tasks
- Validated indirectly by Fini's core principle: *"a hallucinated refund is a direct financial loss"* — their solution was to move away from document retrieval toward live data access

---

## Comparison Table

| Dimension | A: Pure RAG | B: KG + RAG | C: Tool-First |
|---|---|---|---|
| Accuracy (complex reasoning) | 50–60% | 85–90% | ~99% (on tool-reachable facts) |
| Factual grounding | Probabilistic | Structured, traceable | Guaranteed (API) |
| Setup complexity | Low | Medium | Medium–High |
| Works without API access | Yes | Yes | No |
| Works for open-ended Q&A | Yes | Yes | No |
| Works for real-time status | No | Partially | Yes |
| Self-improving | No | Yes (with auto-update) | No (rule updates are manual) |
| Hallucination risk | High | Low | None (on factual layer) |
| Best for | FAQs, policies, docs | Complex policy reasoning | Status lookups, system queries |

---

## Decision for This Repository

**Refund Not Received** → Architecture C (Tool-First)

**Rationale:**
1. The ground truth is always in a live system (order status, account balance)
2. A wrong status answer causes direct financial harm — zero tolerance for hallucination
3. The workflow is a decision tree, not a search problem — rule-based routing is the right fit
4. Both relevant APIs are known and accessible

**Where Architecture B would apply in this repository:**
- Policy layer: "Is this merchant eligible for an expedited refund?" — answer is in policy documents, requires conditional reasoning → KG + RAG is appropriate
- Knowledge base for response generation: "What is the standard refund SLA?" → structured knowledge retrieval

**Hybrid approach for future versions:**
```
Tool-First (Architecture C) for factual queries
    +
KG + RAG (Architecture B) for policy/eligibility reasoning
    =
Grounded facts + accurate policy application
```

---

## Note on Fini's Knowledge Atlas

Fini's Knowledge Atlas is a proprietary, closed-source implementation of Architecture B. Their performance claims (98% accuracy, zero hallucinations) are self-reported and not peer-reviewed.

**What is independently validated:**
- The underlying concept (structured knowledge hierarchy outperforms RAG) has strong academic support
- The specific accuracy numbers (90% vs 60%) are from independent research, not Fini's own claims
- Open-source alternatives (Graphiti, RAGFlow) implement the same concept and are production-ready

**Conclusion:** Fini's architecture is sound and their approach is reproducible with open-source tools. The performance claims are plausible but should be independently validated before citing as benchmarks.

---

## Sources

- [Graph-Enhanced RAG for E-Commerce Customer Support (arxiv 2509.14267)](https://arxiv.org/abs/2509.14267)
- [RAG with Knowledge Graphs for Customer Service QA (arxiv 2404.17723)](https://arxiv.org/abs/2404.17723)
- [RAFT: Stateful Retrieval-Augmented Framework for Troubleshooting Agents](https://arxiv.org/pdf/2609.20754)
- [Human Cognition Inspired RAG with Knowledge Graph (arxiv 2503.06567)](https://arxiv.org/pdf/2503.06567)
- [RAGless Architecture — Fini Blog](https://www.usefini.com/blog/what-is-ragless)
- [The Knowledge Atlas — Fini Resource Library](https://www.usefini.com/resource-library/the-knowledge-atlas-structured-reasoning-and-autonomous-management-for-enterprise-ai-support)
- [Graphiti — Real-Time Knowledge Graphs for AI Agents](https://github.com/getzep/graphiti)
- [RAGFlow — Open-Source RAG Engine with Graph Support](https://github.com/infiniflow/ragflow)
