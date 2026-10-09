# Enterprise Support Agent

> **Enterprise AI Delivery Reference**
> A work-in-progress reference repository documenting how to discover and design enterprise AI workflows, with implementation, evaluation, and deployment planned.

---

## The Problem

Most enterprise AI demos can answer questions.

Production systems must also retrieve verified data, call business APIs, respect permissions, handle failures, escalate uncertain cases, and be continuously evaluated.

This repository documents a proposed approach to closing that gap. Design artifacts are available; implementation and measured results are not yet published.

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

这是一个支付行业B2B退款未到账技术支持场景的**方案设计案例（尚未验证生产效果）**：
通过结构化 Discovery 评估 AI 适合性，梳理人工工作流；
提出基于业务API、确定性路由和人工接管的架构与风险控制方案；
定义功能、安全、性能的验收标准与测试计划。
**效率改善、成本下降和客诉改善均为待验证目标，而非已取得的成果。**

| 文档 | 内容 |
|---|---|
| [discovery.md](examples/refund-not-received/discovery.md) | AI 适合性评估（自定义评分19/21，非外部认证） |
| [workflow.md](examples/refund-not-received/workflow.md) | 人工流程与拟议AI流程、升级 payload 结构 |
| [architecture.md](examples/refund-not-received/architecture.md) | 拟议组件与技术选型（非已运行实现） |
| [risks.md](examples/refund-not-received/risks.md) | 10 个设计风险及拟议缓解措施（尚待测试） |
| [acceptance.md](examples/refund-not-received/acceptance.md) | F1–F10 功能标准、S1–S5 安全标准及160条拟议测试用例 |

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

## Demo Status

A runnable demo is **not yet released**. Agent workflow, connectors, evaluation and deployment remain planned. The sample message below is a proposed future test input, not evidence of a working deployment:

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
| Example: Refund Not Received (design documents) | Available; implementation pending |
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
