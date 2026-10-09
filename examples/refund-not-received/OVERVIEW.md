# Refund Not Received — case overview

> Scope: B2B merchant support at a payment provider. **This is a design and implementation prototype, not verified production ROI.**

## Problem
A merchant reports the buyer has not received a refund. Support must verify identifiers and check order/refund and sometimes account/channel evidence. A retrieved status is **not** proof that the buyer received funds or that the issue is resolved.

## Job to be done
Give the merchant a truthful, evidence-backed status and next step while minimizing repeated cross-system investigation.

## Proposed solution
- Parse support text and clarify order ID.
- Use authorized read-only business tools to retrieve refund and account state.
- Use deterministic routing for clear statuses and failures.
- Escalate ambiguity, tool errors, channel investigations and any money-moving request with structured context.
- Log evidence and validate outputs before merchant-facing communication.

## Current evidence
- **Documented:** business discovery, workflows, risk controls, acceptance targets.
- **Code present:** LangGraph agent, mock connectors, unit/safety/integration tests.
- **Not established in this document:** successful full test execution, production deployment, real-system integration, realized time saving, ROI or reduction of complaints.
- Historical estimate: straightforward cases about five minutes; complex cases can require half a day of work. These are practitioner observations, not a measured benchmark.
- The suitability score 19/21 is a project-specific judgment rubric, not an external certification.

## Read next
- [Workflow & architecture](workflow.md)
- [Evaluation & risks](evaluation.md)
- [Repository root](../../README.md)
