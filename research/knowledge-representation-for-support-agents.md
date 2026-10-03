# Knowledge Representation for Support Agents

> **Last updated:** 2026-10-03
> **Scope:** How to represent domain knowledge for AI support agents — RAG, knowledge graphs, structured workflows
> **Purpose:** Justify the tool-first architecture choice in this repository and document the trade-offs

> **Correction note (2026-10-03):** An earlier version of this document stated "structured reasoning outperforms vector RAG." This was imprecise. The accurate community consensus is: **query type determines architecture**. Structured/graph approaches win on multi-hop reasoning; vector RAG wins on single-hop fact retrieval; tool-first bypasses retrieval entirely for real-time status queries. See the Comparison Table below.

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

> **Important nuance:** No single architecture wins across all query types. The data below reflects each approach's strength zone, not a universal ranking.

| Dimension | A: Pure RAG | B: KG + RAG | C: Tool-First |
|---|---|---|---|
| Accuracy — single-hop fact retrieval | **High** | High | N/A (no retrieval) |
| Accuracy — multi-hop reasoning | 50–60% | **85–90%** | N/A (no retrieval) |
| Accuracy — real-time status queries | Low (no live data) | Low (no live data) | **~99%** |
| Factual grounding | Probabilistic | Structured, traceable | Guaranteed (API) |
| Setup complexity | Low | Medium | Medium–High |
| Works without API access | Yes | Yes | No |
| Works for open-ended Q&A | Yes | Yes | No |
| Works for real-time status | No | No | **Yes** |
| Self-improving | No | Yes (with auto-update) | No |
| Hallucination risk | High | Low | None (on factual layer) |
| Cost per query | $0.001 | $0.005–0.01 | $0.01–0.05 |
| Latency | 100–500ms | 500ms–2s | 2–10s |
| **Best for** | FAQs, policies, static docs | Policy reasoning, eligibility, multi-hop | Status lookups, live system queries |

**Community consensus (2025–2026):** Use Vector RAG as default. Add GraphRAG when queries require relational reasoning. Use Tool-First when ground truth lives in a live API. Hybrid is normal in production.

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

---

## Extended Community Consensus (2025–2026)

Beyond the RAG vs GraphRAG debate, five additional consensus points directly affect this repository's design.

---

### Consensus 1: Deterministic routing reduces LLM cost by 93%

**Source:** Graph-Based Self-Healing Tool Routing ([arxiv 2603.01548](https://arxiv.org/pdf/2603.01548))

> Separating concerns: monitors produce priority signals, graph routing handles routine decisions, LLM is invoked only when the graph returns no path. Reduces control-plane LLM calls by **93%** in benchmarks.

**Applied in this repo:** The Result Router in `architecture.md` is a deterministic rule engine — no LLM involved in routing decisions. The LLM handles intent classification and response generation only.

---

### Consensus 2: Tool calling and RAG solve different problems

**Source:** [RAG vs. Tool-Calling Agents (HuggingFace Blog)](https://huggingface.co/blog/prismberry-technologies/rag-vs-tool-calling-agents)

> RAG helps an AI find and use relevant information from a knowledge base. Tool calling allows an AI to interact with external systems and perform operations. They are complementary, not competing.

**Applied in this repo:** Architecture C (Tool-First) for live status queries. Architecture B (KG+RAG) reserved for policy reasoning in future versions. Neither replaces the other.

---

### Consensus 3: Anthropic's 5 agentic workflow patterns

**Source:** [Anthropic Agentic Design Patterns](https://www.anthropic.com/engineering/claude-code-best-practices) + [MindStudio analysis](https://www.mindstudio.ai/blog/claude-design-6-agentic-patterns-vertical-ai-apps)

The five composable patterns now recognized as the standard vocabulary:

| Pattern | Description | Used in this repo |
|---|---|---|
| Prompt Chaining | Output of one LLM call → input of next | Intent → Collect → Generate |
| **Routing** | Classify input → direct to specialized handler | Result Router (deterministic) |
| Parallelization | Run multiple LLM calls simultaneously | — (future: multi-system query) |
| Orchestrator-Workers | Orchestrator directs specialist agents | Agent Orchestrator |
| Evaluator-Optimizer | One LLM evaluates another's output | — (planned: eval suite) |

**Applied in this repo:** Routing + Orchestrator-Workers are the primary patterns. Routing is intentionally deterministic (not LLM-based) for the result classification step.

---

### Consensus 4: Symbolic guardrails, not prompt-based guardrails

**Source:** [Don't Make Models Guess Security: Symbolic Guardrails for Domain-Specific AI Agents (arxiv 2604.15579)](https://arxiv.org/pdf/2604.15579)

> LLM-based guardrails are probabilistic — a sufficiently crafted prompt can bypass them. For high-stakes domains, symbolic (code-enforced) guardrails are required.

**Applied in this repo:** The "no write operations" constraint is enforced at the code level — the tool layer has no write methods. This is not a prompt instruction. It cannot be bypassed by a merchant's message.

---

### Consensus 5: Agentic RAG cost/latency tradeoff is real

**Source:** [Agentic RAG in 2026: Patterns, Code, Observability (FutureAGI)](https://futureagi.com/blog/agentic-rag-systems-2025/)

> Naive RAG: $0.001/query, 100–500ms. Agentic RAG (tool-calling): $0.01–0.10/query, 2–10s. The cost is 10–100x higher. This is acceptable for high-value enterprise support tickets, not for consumer chatbots.

**Applied in this repo:** The acceptance criteria targets < $0.05/session and < 4s P95 latency — calibrated to the enterprise support context where each ticket has non-trivial human cost. The cost premium is justified by the automation of $50+ human effort per complex case.

---

## Sources

- [Graph-Enhanced RAG for E-Commerce Customer Support (arxiv 2509.14267)](https://arxiv.org/abs/2509.14267)
- [RAG with Knowledge Graphs for Customer Service QA (arxiv 2404.17723)](https://arxiv.org/abs/2404.17723)
- [RAG vs. GraphRAG: A Systematic Evaluation (arxiv 2502.11371)](https://arxiv.org/html/2502.11371v3)
- [Do We Still Need GraphRAG? (arxiv 2604.09666)](https://arxiv.org/html/2604.09666v1)
- [RAFT: Stateful Retrieval-Augmented Framework for Troubleshooting Agents](https://arxiv.org/pdf/2609.20754)
- [Graph-Based Self-Healing Tool Routing (arxiv 2603.01548)](https://arxiv.org/pdf/2603.01548)
- [Symbolic Guardrails for Domain-Specific AI Agents (arxiv 2604.15579)](https://arxiv.org/pdf/2604.15579)
- [Microsoft GraphRAG open source announcement](https://www.microsoft.com/en-us/research/blog/graphrag-new-tool-for-complex-data-discovery-now-on-github/)
- [microsoft/graphrag-benchmarking-datasets](https://github.com/microsoft/graphrag-benchmarking-datasets)
- [RAG vs. Tool-Calling Agents — HuggingFace Blog](https://huggingface.co/blog/prismberry-technologies/rag-vs-tool-calling-agents)
- [Agentic RAG in 2026: Patterns, Code, Observability — FutureAGI](https://futureagi.com/blog/agentic-rag-systems-2025/)
- [Anthropic Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [RAGless Architecture — Fini Blog](https://www.usefini.com/blog/what-is-ragless)
- [Graphiti — Real-Time Knowledge Graphs for AI Agents](https://github.com/getzep/graphiti)
- [RAGFlow — Open-Source RAG Engine with Graph Support](https://github.com/infiniflow/ragflow)
