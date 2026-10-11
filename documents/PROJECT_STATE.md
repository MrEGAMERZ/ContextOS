# ContextOS: Multi-Agent Project State & Coordination Document

> **Single Source of Truth** for all autonomous agents and contributors.
> **Last Updated:** 2026-10-11
> **Repository:** `/Users/rehan/Developer/AmazonHack`
> **Primary Hackathon Track:** Alexa+ (Self-Hosted MCP Server)
> **Mini-Challenges:** AWS Builder (Bedrock + Agentic Reasoning)

---

## 1. System Overview & Vision

**ContextOS** is an ambient contextual intelligence platform that transforms raw smart-home sensor feeds into a queryable, semantic **Memory Graph**. 

Unlike conventional smart home hubs (like Home Assistant, Ring, or Alexa routines) that rely on static if-this-then-that triggers, ContextOS understands **why** events occur, maintains persistent entity relationships over time, detects behavioral omissions (e.g., missed routines or open doors), and provides natural voice-driven recall.

### Core Product Capabilities (Hackathon MVP):
1. **Semantic Memory Graph**: PostgreSQL-backed graph tracking entities (people, devices, locations), directional relationships, and timestamped event streams.
2. **Alexa+ Voice Interface (Primary Track)**: Self-hosted Model Context Protocol (MCP) server allowing users to ask natural questions like *"Where are my glasses?"* or *"Was the front door left open last night?"*.
3. **Caregiver Trust Dashboard**: Real-time Next.js + React Flow visualizer rendering nodes and edges as events occur, building transparent trust.
4. **"Why Did You Do That?" Audit Trail**: Bedrock (Claude 3.5 Sonnet) reasoning logs with extracted `<thinking>` steps explaining every automated alert.
5. **Simulated Event Injector & Fallback**: Web-based event injection panel to guarantee fail-safe live demo execution, with an approved Simulated Alexa+ Voice Harness fallback.

---

## 2. What Has Been Done (Completed)

| Milestone | Status | Details |
|---|---|---|
| **Git Repository & Rules** | ✅ Complete | Initialized git on `main`, committed `IDEA.md`, configured `.gitignore`, and set up gstack rules in `CLAUDE.md`. |
| **Problem & Premise Alignment** | ✅ Complete | Ran `/office-hours`, challenged premises, established value in semantic memory rather than building another hardware adapter hub. Produced `DESIGN.md`. |
| **CEO Plan Review (/plan-ceo-review)** | ✅ Complete | Locked into `SCOPE EXPANSION` mode. Added 5 killer hackathon features (Visual Graph UI, CoT Endpoint, Event Injector, Voice Interface, Anomaly Engine). |
| **Amazon Track Selection** | ✅ Complete | Locked **Alexa+ Track** via Self-Hosted MCP Server. Relegated Ring/Fire TV/Bee to post-hackathon scope. |
| **Dual-Tier Model Latency Architecture** | ✅ Complete | Solved Alexa's strict 8-second voice turn SLA: <br>• **Voice Path (<2s SLA)**: Pure deterministic SQL lookups in MCP tools (<50ms) with lightweight models.<br>• **Async Reasoning Path**: Bedrock Claude 3.5 Sonnet processing background graph updates and `<thinking>` audit logs. |
| **Persistence Schema Design** | ✅ Complete | Defined complete PostgreSQL DDL: `entities`, `relationships`, `events`, and `action_audit_logs`. |
| **Adversarial Spec Review** | ✅ Complete | Completed 3 rigorous subagent review iterations; resolved all contradictions, voice timeouts, and schema mismatches. Verified `## GSTACK REVIEW REPORT` attached to `IDEA.md`. |
| **Clean Repository Infrastructure** | ✅ Complete | Configured comprehensive `.gitignore` filtering out OS artifacts, Python caches, Node modules, databases, logs, secrets, and agent directories. |

---

## 3. What Needs To Be Done (Active Implementation Tasks)

The implementation is broken down into structured, parallelizable workstreams for agents:

### Workstream 1: Database & Persistence Layer (`context_os/db`)
- [ ] Initialize PostgreSQL Docker container (`docker-compose.yml`) with persistent volume.
- [ ] Set up SQLAlchemy 2.0 async engine and session management.
- [ ] Write declarative models matching the verified schema:
  - `Entity`: `id`, `name`, `entity_type`, `metadata`, `created_at`, `updated_at`.
  - `Relationship`: `id`, `source_entity_id`, `target_entity_id`, `relation_type`, `weight`, `metadata`, `updated_at`.
  - `Event`: `id`, `event_type`, `source_device`, `payload`, `occurred_at`.
  - `ActionAuditLog`: `id`, `action_type`, `trigger_event_id`, `prompt_context`, `thinking_process`, `output_response`, `created_at`.
- [ ] Implement database indexes on `relationships(source_entity_id, relation_type)` and `events(occurred_at)`.
- [ ] Seed initial home baseline entities (rooms, primary users, known objects like "glasses", "medicine").

### Workstream 2: Core Context & Ingestion Engine (`context_os/engine`)
- [ ] Build Event Normalizer: Ingest incoming raw events and update graph state:
  - Example: `door_opened` event updates `front_door.state = "open"`.
  - Example: `object_detected` event updates `glasses.located_in -> living_room_table`.
- [ ] Implement Anomaly & Temporal Omission Engine:
  - Immediate state-change rule evaluation (e.g., door opened during restricted hours).
  - 60-second scheduled heartbeat tick detecting omissions (e.g., `front_door.state == 'open'` for > 30 minutes, or absence of expected morning movement).

### Workstream 3: Self-Hosted MCP Server & API (`context_os/mcp` & `context_os/api`)
- [ ] Scaffold FastAPI backend app with CORS and standard error handlers.
- [ ] Implement fast, deterministic MCP Tool Handlers (<50ms execution):
  - `get_entity_context(entity_name: str)`: 2-hop graph neighborhood retrieval.
  - `get_recent_events(limit: int = 10, event_type: Optional[str] = None)`: Recent timeline query.
  - `query_memory_graph(query: str)`: Natural language or keyword semantic retrieval.
- [ ] Implement SSE / HTTP transport endpoints required for Alexa+ tool binding.
- [ ] Add public tunnel scripts (`cloudflared` / `ngrok`) for local live Alexa testing.
- [ ] Build REST endpoints for the frontend:
  - `GET /api/graph`: Returns active nodes and edges for React Flow.
  - `GET /api/events/stream`: Server-Sent Events (SSE) broadcasting real-time graph events.
  - `POST /api/events/inject`: Receives synthetic events from the Injector panel.
  - `GET /api/audit`: Returns recent Bedrock reasoning chains.

### Workstream 4: Amazon Bedrock Integration (`context_os/ai`)
- [ ] Configure `boto3` Bedrock client targeting AWS region with Claude 3.5 Sonnet enabled.
- [ ] Implement asynchronous context reasoning service:
  - Formulate structured prompt embedding entity subgraphs.
  - Enforce system prompt requiring `<thinking>...</thinking>` XML tags.
  - Regex extraction parser to store thinking in `action_audit_logs.thinking_process`.

### Workstream 5: Caregiver Trust Dashboard (`frontend/`)
- [ ] Initialize Next.js 14+ (App Router) with Tailwind CSS and Lucide icons.
- [ ] Implement React Flow canvas visualizing the ContextOS Memory Graph (Rooms, Devices, People, Objects).
- [ ] Connect SSE stream (`/api/events/stream`) to animate nodes and edges in real time.
- [ ] Build Reasoning Drawer / Audit Log viewer rendering Claude's `<thinking>` chain of thought.

### Workstream 6: Simulated Event Injector & Voice Harness (`frontend/` & `tests/`)
- [ ] Build web UI control panel with one-click trigger buttons:
  - "Ringing Doorbell"
  - "Front Door Left Open"
  - "Move Glasses to Kitchen Table"
  - "Kitchen Motion at 2 AM"
- [ ] Implement Simulated Alexa+ Voice Harness:
  - Text and voice-input widget that talks directly to the MCP tools, guaranteeing an end-to-end interactive pitch even without active Alexa hardware.
- [ ] Write automated integration test script running the complete 3-minute hackathon demo script.

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
