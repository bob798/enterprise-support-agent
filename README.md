# Enterprise Support Agent

> **Enterprise AI Delivery Reference**
> A practical repository showing how to discover, design, build, evaluate, and deploy enterprise AI workflows.

---

## The Problem

Most enterprise AI demos can answer questions.

Production systems must also retrieve verified data, call business APIs, respect permissions, handle failures, escalate uncertain cases, and be continuously evaluated.

This repository demonstrates how to close that gap.

---

## What This Repository Demonstrates

- Discover an enterprise AI opportunity
- Map the existing business workflow
- Decide where AI should and should not be used
- Integrate CRM, knowledge, and business APIs
- Build a controlled agent workflow
- Evaluate quality, safety, latency, and cost
- Add guardrails and human approval
- Deploy, observe, and continuously improve the system

---

## Reference Architecture

```
Support Channel
  → Agent Workflow
    → Knowledge + CRM + Business Tools
      → Policy & Guardrails
        → Response / Human Handoff
          → Evaluation & Observability
```

---

## Examples

### Refund Not Received — 支付退款失败工单 AI 改造

完整展示了支付行业客服岗位退款失败工单的 AI 改造过程：
通过结构化 Discovery 评估 AI 适合性，梳理现有工作流和业务流；
基于金融行业风险属性推导架构约束，用 AI 重构工作流；
提升了系统自动化能力和工单处理效率，降低了人力成本；
同时把对外服务一致性从管理承诺变成架构层保证，降低了客诉率和人员培训成本。
整套方法论可复用到同类 AI 改造项目。

| 文档 | 内容 |
|---|---|
| [discovery.md](examples/refund-not-received/discovery.md) | AI 适合性评估，19/21 分，行业基准对比 |
| [workflow.md](examples/refund-not-received/workflow.md) | 11 步人工流程，3 个 AI 介入点，升级 payload 结构 |
| [architecture.md](examples/refund-not-received/architecture.md) | 技术选型依据，LangGraph + Claude + FastAPI |
| [risks.md](examples/refund-not-received/risks.md) | 10 个风险，R3 分 9/9，每个风险的缓解措施 |
| [acceptance.md](examples/refund-not-received/acceptance.md) | F1–F10 功能标准，S1–S5 安全标准，160 个测试用例 |

---

### Charged After Cancellation — 取消订阅后仍扣费（计划中）

| Example | Business Problem | Systems |
|---|---|---|
| [Charged After Cancellation](examples/charged-after-cancellation/) | 取消订阅后仍扣费 | Support + CRM + Billing + Subscription |

---

## Delivery Method

This repository uses the **Enterprise AI Delivery Loop** — a five-phase method for taking an enterprise AI workflow from problem to production.

```
Discover → Design → Build → Validate → Operate → (back to Discover)
```

| Phase | Goal | Key Output |
|---|---|---|
| [01 Discover](framework/01-discover/) | Find problems worth solving with AI | Opportunity assessment, workflow inventory |
| [02 Design](framework/02-design/) | Design a controlled AI workflow | Tool contracts, guardrails, acceptance criteria |
| [03 Build](framework/03-build/) | Deliver a working vertical slice | Agent graph, connectors, demo |
| [04 Validate](framework/04-validate/) | Prove reliability with evidence | Golden dataset, eval results, release gate |
| [05 Operate](framework/05-operate/) | Run and improve in production | Monitoring, feedback loop, business metrics |

---

## Run the Demo

```bash
docker compose up
```

Then send a test message:

```
My refund for order #10248 has not arrived. It has been 7 days.
```

---

## Evaluation Results

> Status: in progress — results will be published after v0.1 release.

| Metric | Target | Result |
|---|---|---|
| Tool call accuracy | > 90% | — |
| Factual groundedness | > 95% | — |
| Handoff accuracy | > 92% | — |
| Unauthorized action rate | 0% | — |
| P95 latency | < 4s | — |
| Cost per session | < $0.05 | — |

---

## Project Status

| Component | Status |
|---|---|
| Delivery method (framework/) | In progress |
| Example: Refund Not Received | In progress |
| Example: Charged After Cancellation | Planned |
| Agent workflow (agent/) | Planned |
| CRM + Payment connectors | Planned |
| Evaluation suite (evals/) | Planned |
| Observability (observability/) | Planned |
| Docker deployment | Planned |

---

## Repository Structure

```
enterprise-support-agent/
├── framework/          # Delivery method templates (5 phases)
├── examples/           # Worked examples with discovery → results
│   ├── refund-not-received/
│   └── charged-after-cancellation/
├── agent/              # Agent workflow implementation
├── connectors/         # CRM, payment, subscription API connectors
├── tools/              # Tool definitions for agent
├── knowledge/          # Knowledge base content
├── evals/              # Evaluation datasets and test suites
├── observability/      # Tracing and monitoring config
├── deployment/         # Docker, CI/CD
└── tests/              # Integration and regression tests
```

---

## Who Is This For

- AI engineers building enterprise automation
- Solutions architects evaluating agentic systems
- Field delivery engineers (FDE) planning AI rollouts
- Anyone who wants to see enterprise AI beyond the demo stage
