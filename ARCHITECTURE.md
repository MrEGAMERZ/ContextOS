# ContextOS — Production Architecture & Plugin System

> **Hackathon Deadline:** Oct 23, 2026 | **Track:** Alexa+ MCP · AWS Builder
> **Design Principle:** ContextOS is a *semantic intelligence core* — not an Alexa app, not a home assistant. It is a **pluggable platform** that any voice assistant, app, or device ecosystem can connect to.

---

## System Overview

```
╔══════════════════════════════════════════════════════════════════════╗
║                    ADAPTER LAYER  (Plugin System)                   ║
║  ┌──────────────┐ ┌─────────────────┐ ┌──────────────────────────┐  ║
║  │  Alexa+ MCP  │ │ Google Home MCP │ │  REST / Webhook Adapter  │  ║
║  │  (PRIMARY)   │ │   (FUTURE)      │ │  (Any HTTP client)       │  ║
║  └──────┬───────┘ └────────┬────────┘ └───────────┬──────────────┘  ║
╚═════════╪═════════════════╪═════════════════════════╪════════════════╝
          │                 │                         │
          ▼                 ▼                         ▼
╔══════════════════════════════════════════════════════════════════════╗
║              CONTEXTOS CORE  (FastAPI · localhost:8000)             ║
║                                                                      ║
║  ┌──────────────┐  ┌────────────────┐  ┌───────────────────────┐   ║
║  │ Ingestion    │  │ Anomaly Engine │  │   AI Reasoning Layer  │   ║
║  │ Engine       │  │ SQL + 60s tick │  │  Bedrock Haiku/Sonnet │   ║
║  └──────┬───────┘  └───────┬────────┘  └──────────┬────────────┘   ║
║         └──────────────────┴───────────────────────┘               ║
║                             │                                        ║
║              ┌──────────────▼───────────────┐                       ║
║              │      Memory Graph DB          │                       ║
║              │  entities / relationships     │                       ║
║              │  events / action_audit_logs   │                       ║
║              └──────────────────────────────┘                       ║
╚══════════════════════════════════════════════════════════════════════╝
          │                                    │
          ▼                                    ▼
  SSE Event Stream              Caregiver Trust Dashboard (Next.js)
  (real-time graph updates)     React Flow · Voice Harness · CoT Drawer
```

---

## Three-Tier Product Breakdown

### Tier 1 — Foundation ✅ (DONE)
The platform can run standalone with zero external dependencies.

| Component | File | Status |
|---|---|---|
| Memory Graph PostgreSQL schema | `backend/app/models/` | ✅ Done |
| SQLAlchemy 2.0 async ORM | `backend/app/database.py` | ✅ Done |
| FastAPI REST server | `backend/app/main.py` | ✅ Done |
| Household seed data (Arthur, Ravi, Sarah, Alexa, Glasses, Medicine) | `backend/app/seed.py` | ✅ Done |
| 15 automated tests | `backend/tests/` | ✅ Done |
| Production `.gitignore` | `.gitignore` | ✅ Done |

### Tier 2 — Core Features ✅ (DONE / IN PROGRESS)
The platform understands events, reasons about them, and responds.

| Component | File | Status |
|---|---|---|
| Event Ingestion Engine | `backend/app/engine/ingestion.py` | ✅ Done |
| Anomaly + Omission Engine (60s tick) | `backend/app/engine/anomaly.py` | ✅ Done |
| Simulated Event Injector (4 scenarios) | `backend/app/engine/injector.py` | ✅ Done |
| SSE Event Stream | `backend/app/engine/stream.py` | ✅ Done |
| Self-Hosted MCP Server (3 tools) | `backend/app/mcp/server.py` | ✅ Done |
| Bedrock Dual-Tier AI (Haiku + Sonnet) | `backend/app/ai/` | ✅ Done |
| Caregiver Dashboard (Next.js) | `frontend/app/page.tsx` | ✅ Done |
| React Flow live graph visualizer | `frontend/app/page.tsx` | ✅ Done |
| Voice Harness Simulator | `frontend/app/page.tsx` | ✅ Done |
| Audit Log / CoT drawer | `frontend/app/page.tsx` | ✅ Done |

### Tier 3 — Extra Features 🔲 (Backlog)
Makes ContextOS a real product, not just a hackathon prototype.

| Component | Status | Est. Effort |
|---|---|---|
| Cloudflare Tunnel + real Alexa+ MCP registration | 🔲 Backlog | 1h |
| Docker Compose (one-command stack) | 🔲 Backlog | 1h |
| Adapter Plugin Interface (`BaseAdapter` abstract class) | 🔲 Backlog | 2h |
| Multi-home / Multi-tenant support | 🔲 Backlog | 4h |
| Real AWS Bedrock credentials + production test | 🔲 Backlog | 30m |
| Computer Vision perception pipeline | 🔲 Backlog | 8h |
| Alexa Skills Marketplace submission | 🔲 Backlog | post-hackathon |

---

## Adapter Plugin System (How It Becomes Multi-Platform)

The core insight: the Memory Graph and AI Reasoning Layer are 100% platform-agnostic. Every voice assistant or device ecosystem is just **an adapter** that reads from and writes to the same core engine.

```python
# context_os/adapters/base.py — the interface every plugin implements

from abc import ABC, abstractmethod
from typing import Optional

class ContextOSAdapter(ABC):
    """
    Implement this interface to connect any device ecosystem,
    voice assistant, or app to ContextOS.

    Examples:
        - AlexaMCPAdapter   → MCP HTTP endpoint Alexa+ calls
        - GoogleHomeAdapter → Google Home Actions on Google
        - HomeKitAdapter    → Apple HomeKit bridge (MFi)
        - RESTAdapter       → Generic webhook / REST client
        - CLIAdapter        → Terminal query tool
    """

    @abstractmethod
    async def get_entity_context(self, entity_name: str) -> dict:
        """Return 2-hop neighborhood of an entity from the Memory Graph."""
        ...

    @abstractmethod
    async def get_recent_events(self, limit: int = 10, event_type: Optional[str] = None) -> list:
        """Return recent smart-home events from the event log."""
        ...

    @abstractmethod
    async def query_memory(self, query: str) -> dict:
        """Semantic natural language query over the Memory Graph."""
        ...

    @abstractmethod
    async def ingest_event(self, event_type: str, source: str, payload: dict) -> None:
        """Ingest a new smart-home event and trigger graph mutation."""
        ...
```

To add support for **Google Home**, **Apple HomeKit**, or **Nest**:
1. Create `backend/app/adapters/google_home.py` implementing `ContextOSAdapter`.
2. Register it with the FastAPI app as a new router.
3. Done — the Memory Graph, Anomaly Engine, and AI Layer need zero changes.

---

## Deployment

### Hackathon (Today)
```bash
# Backend
backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend

# Frontend
cd frontend && npm run dev

# Expose to Alexa+ (when needed)
cloudflared tunnel --url http://localhost:8000
```

### Production (AWS)
| Service | Role | Notes |
|---|---|---|
| AWS App Runner | Backend container | Public HTTPS URL, auto-scale |
| Amazon RDS PostgreSQL | Database | Change 1 env var from SQLite |
| AWS Bedrock (same region) | AI inference | Sub-100ms latency |
| Vercel | Frontend | Free tier, `git push` deploy |

---

## API Surface (What Adapters Call)

| Endpoint | Method | Purpose |
|---|---|---|
| `/mcp/sse` | GET | MCP SSE transport for Alexa+ |
| `/api/graph/entities` | GET | List all graph entities |
| `/api/graph/entities/{name}/neighborhood` | GET | 2-hop context |
| `/api/graph/relationships` | GET | All edges |
| `/api/events/inject` | POST | Inject a synthetic scenario |
| `/api/events/stream` | GET | SSE real-time event stream |
| `/api/events/recent` | GET | Recent event log |
| `/api/agent/query` | POST | Natural language query |
| `/api/audit-logs` | GET | AI reasoning audit trail |
| `/health` | GET | Health check |

---

## Why This Architecture Is Future-Proof

1. **Adapter pattern** — adding Google Home takes 1 new file, zero core changes.
2. **Protocol-agnostic** — MCP today, OpenAI Function Calling tomorrow, Apple Actions the day after.
3. **DB-portable** — SQLite locally, PostgreSQL in production, same ORM.
4. **AI-swappable** — `BEDROCK_MODEL_ID_FAST` and `BEDROCK_MODEL_ID_DEEP` are env vars. Swap Claude for Llama or GPT-4o without code changes.
5. **Event-driven core** — the graph reacts to events, not polling. Scales to hundreds of sensors without linear cost growth.
