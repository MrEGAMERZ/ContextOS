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

---

## 5. Quickstart & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ (optional, for Next.js development)

### 1. Run the Backend & Live Dashboard (One Command)
```bash
# Navigate to repo
cd /Users/rehan/Developer/AmazonHack

# Activate Python virtual environment
source backend/.venv/bin/activate

# Launch ContextOS
PYTHONPATH=backend uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser to:
- **Caregiver Trust Dashboard & Voice Simulator**: [http://localhost:8000/dashboard](http://localhost:8000/dashboard)
- **Interactive OpenAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **MCP Server Endpoint**: `http://localhost:8000/mcp`

### 2. Run Test Suite
```bash
PYTHONPATH=backend pytest backend/tests -v
```
*Result: 15/15 tests pass in ~0.20s.*

---

## 6. The 3-Minute Hackathon Demo Narrative

Open [http://localhost:8000/dashboard](http://localhost:8000/dashboard) and walk judges through this narrative:

1. **The Ambient Context**:
   - Point out Arthur (78-year-old homeowner living independently), his neighbor Ravi, daughter Sarah, and household objects.
2. **Event Injection — Ravi Arrives**:
   - In the **Simulated Event Injector**, click **"🔔 Neighbor Visits (Ravi)"**.
   - Notice the graph updates in real-time via Server-Sent Events (SSE).
3. **Alexa+ Voice Query**:
   - In the **Simulated Alexa+ Voice Harness**, click **"Ask Alexa+"** with *"Who is at the front door?"*.
   - Alexa speaks: *"That's your neighbor Ravi. You spoke with him yesterday about the garden tomato plants, and he was expected to visit around 4:00 PM."*
   - Latency badge shows `<50ms SLA Pass`.
4. **"Why Did You Do That?" CoT Drawer**:
   - Open the CoT drawer to show the judge the raw Bedrock Claude 3.5 `<thinking>` steps:
     ```text
     1. Entity Resolution: Received query about front door / visitor.
     2. Context Retrieval: Identified entity 'Ravi' (neighbor) and 'Front Porch'.
     3. Relational Verification: Ravi spoke with Arthur yesterday about tomato plants and scheduled a visit for 4 PM.
     4. Confidence Evaluation: Confidence 0.98; known trusted neighbor.
     5. Action: Formulate clear, calming answer confirming identity, relationship, and scheduled reason.
     ```
5. **Safety Omission Detection**:
   - In the Injector, click **"🚪 Door Left Open (35m)"**.
   - The temporal engine evaluates the omission, flags the safety anomaly, invokes Bedrock to analyze the risk, and generates a quiet caregiver check-in notification for Sarah.
