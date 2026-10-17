# ContextOS — Ambient Contextual Intelligence Platform

> **Hackathon Submission:** Build, Ship, Shape: Amazon Developer Hackathon  
> **Primary Track:** **Alexa+** (Self-Hosted Model Context Protocol Server)  
> **Mini-Challenge:** **AWS Builder** (Amazon Bedrock Claude 3.5 Sonnet & Haiku with `<thinking>` Chain of Thought)  
> **Product Concept:** Ambient, context-aware intelligence platform for independent living and daily cognitive assistance.

---

## 1. Executive Summary

Current smart home devices (cameras, doorbells, voice assistants) operate in disconnected silos. A camera knows *"motion was detected"*, a calendar knows *"an appointment exists"*, and a voice assistant answers isolated queries.

When an elderly homeowner living independently hears a doorbell, they don't need a raw notification. They need:
> *"That is your neighbor Ravi. You spoke with him yesterday about the garden tomato plants, and he was expected to visit around 4:00 PM."*

**ContextOS** provides the missing ambient intelligence layer:
$$\text{Perceive} \longrightarrow \text{Understand} \longrightarrow \text{Remember} \longrightarrow \text{Reason} \longrightarrow \text{Assist} \longrightarrow \text{Escalate}$$

ContextOS transforms raw sensor noise into a queryable **Semantic Memory Graph**, exposes high-speed sub-50ms tools to **Alexa+** via the **Model Context Protocol (MCP)**, and utilizes **Amazon Bedrock (Claude 3.5 Sonnet & Haiku)** for dual-tier conversational and deep audit reasoning.

---

## 2. System Architecture

```text
       ┌────────────────────────────────────────────────────────┐
       │                USER & SENSORY ENVIRONMENT               │
       │                                                        │
       │  Ring Video Doorbell    Kitchen Sensor    Alexa Echo   │
       └──────────┬─────────────────────┬───────────────┬───────┘
                  │                     │               │
                  ▼                     ▼               ▼
       ┌────────────────────────────────────────────────────────┐
       │                EVENT INGESTION PIPELINE                │
       │   POST /api/events/ingest  │  Simulated Event Injector │
       └────────────────────────┬───────────────────────────────┘
                                │
                                ▼
       ┌────────────────────────────────────────────────────────┐
       │              CONTEXT ENGINE & MEMORY GRAPH              │
       │                                                        │
       │   Entities (People, Devices, Locations, Objects, Routine)│
       │   Relationships (neighbor_of, visited, located_in)      │
       │   2-Hop Neighborhood Traversal (<5ms)                  │
       └────────────────────────┬───────────────────────────────┘
                                │
            ┌───────────────────┴───────────────────┐
            ▼                                       ▼
┌───────────────────────────────┐       ┌───────────────────────────────┐
│     ALEXA+ MCP SERVER         │       │     AMAZON BEDROCK CORE       │
│                               │       │                               │
│ • get_entity_context()        │       │ • Fast Conversational Tier    │
│ • get_recent_events()         │       │   (Claude 3.5 Haiku, <1.5s)   │
│ • query_memory_graph()        │       │ • Deep Reasoning Tier         │
│   (SLA: <50ms execution)      │       │   (Claude 3.5 Sonnet + CoT)   │
└───────────────┬───────────────┘       └───────────────┬───────────────┘
                │                                       │
                ▼                                       ▼
┌───────────────────────────────────────────────────────────────────────┐
│                     CAREGIVER TRUST DASHBOARD                         │
│                                                                       │
│  • Live Interactive Memory Graph Visualizer                           │
│  • Simulated Event Injector (One-Click Scenario Blast)                │
│  • Simulated Alexa+ Voice Harness                                     │
│  • "Why Did You Do That?" <thinking> Audit Log Inspector             │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 3. Dual-Tier Bedrock Latency Strategy (Voice SLA Safe)

Alexa requires responses in **<8 seconds** for natural voice interaction. ContextOS guarantees strict compliance through a dual-tier separation:

1. **Voice Turn SLA Tier (<1.5s latency)**:
   - **Model**: Claude 3.5 Haiku on Amazon Bedrock (or direct MCP lookup).
   - MCP tools (`get_entity_context`, `query_memory_graph`) query PostgreSQL/SQLite directly in **<50ms** without nested LLM calls.
   - Strict token limit (<250 tokens) delivers natural speech responses instantly.

2. **Asynchronous Deep Reasoning Tier**:
   - **Model**: Claude 3.5 Sonnet on Amazon Bedrock.
   - Operates in background queues for multi-hop graph inferences, temporal omission detection, and caregiver summaries.
   - Enforces structured `<thinking>...</thinking>` XML tags, extracted into `action_audit_logs` for transparent caregiver verification.

---

## 4. 5 Completed Shipments & Roadmap

| Shipment | Scope | Tag | Status | Pull Request |
|---|---|---|---|---|
| **Shipment 1** | **Memory Graph Engine & Database Foundation** (Entities, Relationships, Events, Audit Logs, SQLite/Postgres) | `v0.1.0-shipment1` | ✅ Merged | [PR #1](documents/pull_requests/PR-001-memory-graph-db.md) |
| **Shipment 2** | **Event Ingestion Pipeline & Alexa+ MCP Server** (Streamable HTTP / SSE MCP Protocol, 3 Voice Tools) | `v0.2.0-shipment2` | ✅ Merged | [PR #2](documents/pull_requests/PR-002-event-ingestion-mcp.md) |
| **Shipment 3** | **Dual-Tier Bedrock Agent & Chain-of-Thought Engine** (Claude 3.5 Haiku/Sonnet, `<thinking>` Extractor, Audit Trail) | `v0.3.0-shipment3` | ✅ Merged | [PR #3](documents/pull_requests/PR-003-bedrock-dual-tier-agent.md) |
| **Shipment 4** | **Anomaly & Omission Engine + Simulated Event Injector** (60s Temporal Clock, Routine Checking, Demo Presets) | `v0.4.0-shipment4` | ✅ Merged | [PR #4](documents/pull_requests/PR-004-anomaly-omission-engine.md) |
| **Shipment 5** | **Caregiver Trust Dashboard & Voice Simulator UI** (Interactive UI, React Flow Graph, Live CoT Viewer, Alexa Voice Harness) | `v0.5.0-shipment5` | ✅ Merged | [PR #5](documents/pull_requests/PR-005-dashboard-voice-simulator.md) |
| **Shipment 6** | **Ring Perception Adapter** (Ding, Motion, Person Detection, Device Graph Sync, Threat Levels, Webhook API) | `v0.6.0-shipment6` | ✅ Merged | [PR #6](documents/pull_requests/PR-006-ring-perception-adapter.md) |
| **Shipment 7** | **Advanced Anomaly Engine & Caregiver Daily Briefing** (Wandering, Fall/Inactivity, Adherence Score, Digest) | `v0.7.0-shipment7` | ✅ Merged | [PR #7](documents/pull_requests/PR-007-advanced-anomalies-caregiver-summary.md) |
| **Shipment 8** | **5-Level Permission Barrier & AWS Creds Validator** (Read/Suggest/Confirm/Act/Escalate, STS Health Check) | `v0.8.0-shipment8` | ✅ Merged | [PR #8](documents/pull_requests/PR-008-permission-model-agent-runtime.md) |
| **Shipment 9** | **Next.js Modular Caregiver Dashboard** (Interactive SVG Graph, Web Speech TTS, Pending Confirmations Modal) | `v0.9.0-shipment9` | ✅ Merged | [PR #9](documents/pull_requests/PR-009-nextjs-modular-dashboard.md) |
| **Shipment 10** | **Production Dockerization, CI Pipeline & Submission Package** (Docker Compose, CI, Demo Script, Feedback) | `v0.10.0-shipment10` | ✅ Merged | [PR #10](documents/pull_requests/PR-010-docker-cicd-submission-package.md) |

---

## 5. Quickstart & Installation

### Option A: Docker Compose (Recommended)
Launch the entire ContextOS stack with a single command:
```bash
docker compose up --build -d
```
- **Caregiver Next.js Dashboard**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend & Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### Option B: Local Virtual Environment
```bash
# 1. Backend
cd /Users/rehan/Developer/AmazonHack
source backend/.venv/bin/activate
PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 2. Frontend
cd frontend
npm install
npm run dev
```

---

## 6. Verification & Automated Tests

Run the complete 27-test suite covering graph persistence, MCP latency SLA, Bedrock CoT parsing, Ring webhook normalizer, advanced anomaly sweepers, and the 5-level safety permission gate:
```bash
PYTHONPATH=backend backend/.venv/bin/pytest backend/tests -v
```
```text
============================== 27 passed in 0.28s ==============================
```

---

## 7. Documentation & Hackathon Deliverables

- 📄 **[Devpost Submission Package](docs/SUBMISSION.md)**: Full project architecture, tracks entered, and technical overview.
- 🎬 **[3-Minute Live Demo Pitch Script](docs/DEMO_SCRIPT.md)**: Scene-by-scene script with presenter cues and audio playback walkthrough.
- 📝 **[Developer Friction Log](docs/FRICTION_LOG.md)**: Real-world engineering learnings (Voice SLA, Bedrock CoT parsing, SQLAlchemy async JSON dirty tracking).
- 💬 **[Amazon Product Feedback](docs/PRODUCT_FEEDBACK.md)**: Actionable feedback for the Alexa+ MCP, Ring, and Amazon Bedrock developer teams.
- ⚖️ **[MIT License](LICENSE)**: Open source license.
- 🔄 **[CI/CD Pipeline](ci/ci.yml)**: Continuous integration pipeline specification.

