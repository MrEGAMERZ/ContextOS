# ContextOS: Multi-Agent Project State & Coordination Document

> **Single Source of Truth** for all autonomous agents and contributors.
> **Last Updated:** 2026-10-17
> **Repository:** `MrEGAMERZ/ContextOS`
> **Hackathon Tracks:** Alexa+ (Self-Hosted MCP Server) & Ring Track (Perception/Event Ingestion)
> **Mini-Challenges:** AWS Builder (Bedrock Claude 3.5 Sonnet/Haiku dual-tier reasoning with `<thinking>` Chain of Thought) & Open Source (MIT)

---

## 1. System Overview & Vision

**ContextOS** is an ambient contextual intelligence platform that transforms raw smart-home sensor feeds into a queryable, semantic **Memory Graph**. 

Unlike conventional smart home hubs (like Home Assistant, Ring, or Alexa routines) that rely on static if-this-then-that triggers, ContextOS understands **why** events occur, maintains persistent entity relationships over time, detects behavioral omissions (e.g., missed routines or open doors), and provides natural voice-driven recall.

### Core Product Capabilities (Hackathon MVP):
1. **Semantic Memory Graph**: PostgreSQL/SQLite-backed graph tracking entities (people, devices, locations), directional relationships, and timestamped event streams.
2. **Alexa+ Voice Interface (Primary Track)**: Self-hosted Model Context Protocol (MCP) server allowing users to ask natural questions like *"Where are my glasses?"* or *"Who is at the door?"* with strict `<50ms` deterministic execution SLA.
3. **Ring Perception Adapter (Co-Primary Track)**: Hardware webhook normalizer mapping chimes, motion zones, and person recognition directly into live graph state with 3-tier threat classification.
4. **Caregiver Trust Dashboard**: Real-time Next.js 14 modular dashboard with interactive SVG graph visualizer, 2-hop neighborhood drawer, and Web Speech API audio synthesis.
5. **"Why Did You Do That?" Audit Trail**: Bedrock (Claude 3.5 Sonnet) reasoning logs with extracted `<thinking>` steps explaining every automated alert.
6. **5-Level Safety Permission Gate**: Read, Suggest, Confirm, Act, Escalate security boundary requiring human confirmation tokens before destructive smart home mutations.
7. **Production DevOps & Docs**: Docker Compose orchestration, automated CI/CD pipeline (`ci/ci.yml`), 3-minute pitch script, friction log, and ecosystem feedback.

---

## 2. What Has Been Done (100% Completed Across 10 Shipments)

| Shipment | Scope | Status | Details |
|---|---|---|---|
| **Shipment 1 (`v0.1.0-shipment1`)** | Database & Persistence Layer | ✅ Complete | SQLAlchemy 2.0 async engine, models (`Entity`, `Relationship`, `Event`, `ActionAuditLog`), seed data, CRUD repo. |
| **Shipment 2 (`v0.2.0-shipment2`)** | Ingestion & Alexa+ MCP Server | ✅ Complete | Event ingestion normalizer, JSON-RPC 2.0 / SSE MCP server, 3 voice tools (`<50ms` SLA). |
| **Shipment 3 (`v0.3.0-shipment3`)** | Dual-Tier Bedrock Agent & CoT | ✅ Complete | Claude 3.5 Haiku/Sonnet routing, `<thinking>` regex extraction, immutable audit logging. |
| **Shipment 4 (`v0.4.0-shipment4`)** | Anomaly Engine & Event Injector | ✅ Complete | 60s temporal clock, door open >30m, missed morning meds, SSE event broadcaster, demo presets. |
| **Shipment 5 (`v0.5.0-shipment5`)** | Caregiver Trust UI Prototype | ✅ Complete | Standalone prototype dashboard (`dashboard.html`), E2E 3-minute pitch verification test. |
| **Shipment 6 (`v0.6.0-shipment6`)** | Ring Perception Adapter | ✅ Complete | Ring webhook router, ding/motion normalization, device hardware sync, threat tiers (LOW/MED/HIGH). |
| **Shipment 7 (`v0.7.0-shipment7`)** | Advanced Anomalies & Briefing | ✅ Complete | Night wandering (23:00-05:00), bathroom fall inactivity (>45m), Autonomy Score (0-100), Bedrock daily briefing. |
| **Shipment 8 (`v0.8.0-shipment8`)** | 5-Level Safety Permission Gate | ✅ Complete | Read/Suggest/Confirm/Act/Escalate policy, confirmation token resolver, AWS STS credentials validator. |
| **Shipment 9 (`v0.9.0-shipment9`)** | Modular Next.js 14 Dashboard | ✅ Complete | Next.js 14 App Router, interactive SVG graph, Web Speech TTS, CoT drawer, safety approval modal. |
| **Shipment 10 (`v0.10.0-shipment10`)** | Docker, CI/CD & Submission | ✅ Complete | Multi-stage Dockerfiles, `docker-compose.yml`, `ci/ci.yml`, MIT License, `docs/` submission suite. |

---

## 3. What Needs To Be Done (Active Implementation Tasks)

The implementation is broken down into structured, parallelizable workstreams for agents:

### Workstream 1: Database & Persistence Layer (`backend/app/models`, `backend/app/database.py`)
- [x] Dual-engine support: SQLite (`aiosqlite`) for zero-friction local run/demo, PostgreSQL (`asyncpg`) for production.
- [x] Set up SQLAlchemy 2.0 async engine and session management.
- [x] Declarative models: `Entity`, `Relationship`, `Event`, `ActionAuditLog`.
- [x] Database indexes on `entities(name, entity_type)`, `relationships(source_entity_id, target_entity_id, relation_type)`, and `events(occurred_at)`.
- [x] Seed initial home baseline entities (Arthur homeowner, Ravi neighbor, Sarah daughter, devices, objects, routines).

### Workstream 2: Core Context & Ingestion Engine (`backend/app/engine/ingestion.py`, `anomaly.py`)
- [x] Event Normalizer: Ingest incoming raw events and update graph state:
  - `doorbell_rung` / `person_detected` updates `last_seen` and links `visited` edge.
  - `object_moved` updates `located_in` edge and `last_seen_location`.
  - `door_opened` / `door_closed` updates entity state.
- [x] Anomaly & Temporal Omission Engine:
  - Immediate state-change rule evaluation.
  - 60-second scheduled heartbeat tick detecting omissions (door open > 30 minutes, missed medication routine).
  - Triggers deep Bedrock Claude 3.5 Sonnet analysis and caregiver notifications.

### Workstream 3: Self-Hosted MCP Server & API (`backend/app/mcp/server.py`, `router.py`)
- [x] Scaffold FastAPI backend app with CORS, health check, and error handlers.
- [x] Fast, deterministic MCP Tool Handlers (<50ms execution SLA):
  - `get_entity_context(entity_name)`: 2-hop graph neighborhood retrieval.
  - `get_recent_events(limit, event_type)`: Recent timeline query.
  - `query_memory_graph(query)`: Semantic and keyword lookup over graph entities.
- [x] Standard Model Context Protocol (MCP) JSON-RPC 2.0 endpoint (`POST /mcp`) for Alexa+ binding.
- [x] REST endpoints for frontend and voice simulation (`POST /api/mcp/call`, `GET /api/mcp/tools`).

### Workstream 4: Amazon Bedrock Integration (`backend/app/ai/bedrock_client.py`, `agent.py`)
- [x] Dual-tier Bedrock architecture:
  - Fast conversational tier: Claude 3.5 Haiku (<250 token budget, <1.5s voice turnaround).
  - Deep reasoning tier: Claude 3.5 Sonnet processing complex subgraphs.
- [x] System prompt enforcing `<thinking>...</thinking>` XML tags and regex extractor.
- [x] Audit trail persistence: Stores exact reasoning steps in `action_audit_logs.thinking_process`.
- [x] Resilient local Bedrock simulator for zero-dependency hackathon testing.

### Workstream 5 & 6: Caregiver Trust Dashboard & Voice Simulator (`backend/app/static/dashboard.html` & `frontend/`)
- [x] Live Interactive Semantic Memory Graph visualizer with real-time SSE animation.
- [x] Interactive 2-Hop Neighborhood Context Inspector.
- [x] Simulated Event Injector panel with instant one-click scenario buttons (Visitor, Glasses, Door Open Anomaly, Missed Medication).
- [x] Simulated Alexa+ Voice Harness with Web Speech TTS audio readout and <50ms Voice SLA benchmark badge.
- [x] "Why Did You Do That?" CoT Drawer displaying raw Bedrock Claude 3.5 `<thinking>` steps.
- [x] Automated end-to-end integration test (`backend/tests/test_e2e_demo_narrative.py`) running the complete 3-minute pitch scenario.

---

## 4. Architectural Rules & Invariants for Agents

1. **Voice Turn SLA is Sacred**:
   - Never call an LLM *inside* a synchronous MCP tool handler.
   - MCP tools must query PostgreSQL directly and return in `<50ms` so Alexa's 8-second speech window is never violated.
2. **Boundary Discipline**:
   - The LLM reasons and suggests; it **never executes destructive smart home mutations** directly without confirmation.
3. **Fail-Safe Demo Rule**:
   - Physical hardware (cameras, real Alexas) is nice to have, but the demo **must be 100% executable and provable** using the Simulated Event Injector and Simulated Voice Harness.
4. **No Inline Imports & Strict Types**:
   - All Python imports at module top.
   - Pydantic models for all API request/response schemas.
   - TypeScript strict mode for the Next.js frontend.

---

## 5. Future Plans & Post-Hackathon Scope

These items were reviewed during the CEO review and formally deferred to post-hackathon versions:
- **Continuous Computer Vision**: Streaming live RTSP camera feeds into multimodal vision models for real-time person recognition.
- **Physical Device Ecosystems**: Official Ring API integrations, Bee wearable Apple Watch sync, and native Fire TV Vega OS ambient visualizer.
- **Cross-Home Multi-Tenancy**: Caregiver SaaS managing dozens of independent homes with role-based access control and HIPAA compliance.
- **Predictive Long-Term Health**: Machine learning models identifying early cognitive or physical decline by tracking subtle routine drift over months.

---

## 6. Directory Structure Target

```
/Users/rehan/Developer/AmazonHack/
├── CLAUDE.md                   # Agent routing rules & guidelines
├── IDEA.md                     # Master concept and verified architecture spec
├── DESIGN.md                   # High-level problem statement & premises
├── documents/
│   └── PROJECT_STATE.md        # THIS FILE (Master Multi-Agent State)
├── .gitignore                  # Production gitignore
├── docker-compose.yml          # PostgreSQL & services containerization
├── pyproject.toml              # Python dependencies & metadata
├── context_os/                 # Python Backend & Engine
│   ├── api/                    # FastAPI REST & SSE endpoints
│   ├── core/                   # Config, settings, logging
│   ├── db/                     # SQLAlchemy models, sessions, migrations
│   ├── engine/                 # Ingestion normalizer & anomaly detector
│   ├── mcp/                    # Self-Hosted MCP server & tool definitions
│   └── ai/                     # AWS Bedrock Claude 3.5 Sonnet client & CoT parser
├── frontend/                   # Next.js Caregiver Trust Dashboard
│   ├── app/                    # Next.js App router
│   ├── components/             # React Flow visualizer, Event Injector, Audit log
│   └── lib/                    # API & SSE clients
└── tests/                      # Pytest suite & integration scenarios
```
