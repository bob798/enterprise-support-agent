# Production Handoff

> **Phase:** Operate
> **Purpose:** Document everything the operations team needs to run this system without the builder present.

---

## System Overview

**What it does:**
**Who uses it:**
**Business impact if down:**

---

## Architecture Summary

| Component | Technology | Where it runs |
|---|---|---|
| Agent | | |
| Knowledge base | | |
| CRM connector | | |
| API layer | | |
| Observability | | |

---

## Access and Credentials

_Do not store credentials here. Reference the secrets manager._

| Secret | Where stored | Who has access |
|---|---|---|
| LLM API key | | |
| CRM API credentials | | |

---

## Runbook

### Start the system

```bash
docker compose up -d
```

### Stop the system

```bash
docker compose down
```

### Check system health

```bash
curl http://localhost:8000/health
```

### View traces

_[Link to observability dashboard]_

---

## SLAs

| Metric | Target | Alert threshold |
|---|---|---|
| Availability | 99% | < 98% over 1 hour |
| P95 latency | < 4s | > 6s for > 5 min |
| Error rate | < 1% | > 3% for > 5 min |

---

## Feedback Loop

- How user feedback is collected:
- How eval dataset is updated:
- Cadence of model/prompt review:
- Who owns continuous improvement:

---

## Known Limitations

- [ ]
- [ ]

---

## Contacts

| Role | Name | Contact |
|---|---|---|
| Builder / Engineer | | |
| Delivery lead | | |
| On-call rotation | | |
