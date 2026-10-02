# Implementation Checklist

> **Phase:** Build
> **Purpose:** Track every component needed for a complete, deployable vertical slice.
> **Rule:** Complete one full end-to-end workflow before adding breadth.

---

## Agent Core

- [ ] Agent graph defined (entry → tools → synthesis → output)
- [ ] System prompt written and reviewed
- [ ] Structured output schema defined
- [ ] Tool calling integrated
- [ ] Error handling for tool failures
- [ ] Streaming responses (if required)

## Tools

- [ ] Tool definitions written (name, description, input schema)
- [ ] Each tool connected to real API or mock
- [ ] Tool output validated against contract
- [ ] Tool errors handled gracefully

## Connectors

- [ ] CRM connector implemented and tested
- [ ] Payment / Billing API connector implemented
- [ ] Knowledge base retrieval implemented
- [ ] Auth / credential management in place (no hardcoded secrets)

## Guardrails

- [ ] Input filter in place
- [ ] Output grounding check in place
- [ ] Human approval flow for write operations
- [ ] PII masking on output

## API Layer

- [ ] POST /chat endpoint available
- [ ] Session management
- [ ] Request/response logging

## Demo UI

- [ ] Basic chat interface running
- [ ] Shows tool call trace (debug mode)
- [ ] Human approval UI for escalated cases

## Deployment

- [ ] Dockerfile written
- [ ] docker-compose.yml includes all services
- [ ] Environment variables documented in .env.example
- [ ] `docker compose up` starts a working system

## Observability

- [ ] Traces captured (LLM calls, tool calls, latency)
- [ ] Errors logged with context
- [ ] Cost tracked per session

---

## Build Sequence

Follow this order to stay in a working state at all times:

1. Stub agent with hardcoded response
2. Connect first tool (read-only)
3. Connect knowledge base
4. Connect second tool
5. Add guardrails
6. Add human approval flow
7. Add observability
8. Dockerize
9. Run acceptance criteria

---

## Definition of Done

- [ ] All acceptance criteria from `02-design/acceptance-criteria.md` pass
- [ ] `docker compose up` starts cleanly from a fresh clone
- [ ] No hardcoded credentials
- [ ] README run instructions are accurate
