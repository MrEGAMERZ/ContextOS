# ContextOS — Devpost Hackathon Submission Package

> **Ambient Contextual Intelligence Platform for Independent Living**  
> **Amazon Developer Hackathon: Build, Ship, Shape 2026**

---

## 🏆 Hackathon Tracks & Challenges Entered

1. **Primary Track: Alexa+ (Self-Hosted Model Context Protocol Server)**
   - Self-hosted MCP Server delivering 3 high-speed semantic memory graph tools over standard JSON-RPC 2.0 / SSE.
   - Enforces strict `<50ms` execution SLA to guarantee Alexa's 8-second speech turnaround window is never violated.
2. **Co-Primary / Perception Track: Ring Track**
   - Full Ring Video Doorbell and Camera Perception Adapter normalizing chimes, motion zones, and person sightings into persistent memory graph context.
   - Real-time threat classification and device battery/connectivity sync.
3. **Mini-Challenge: AWS Builder (Amazon Bedrock Dual-Tier Reasoning)**
   - Dual-tier model routing: **Claude 3.5 Haiku** for conversational voice queries (<250 tokens, <1.5s latency) and **Claude 3.5 Sonnet** for deep anomaly analysis.
   - Rigorous `<thinking>...</thinking>` Chain-of-Thought extraction persisted in immutable audit logs for complete caregiver explainability.
4. **Mini-Challenge: Open Source**
   - Public MIT-licensed repository featuring a reusable semantic memory graph schema, event normalizer, and MCP server.

---

## 💡 Inspiration & Problem Statement

Today, an elderly person living independently might have a Ring doorbell, smart motion sensors, pill dispensers, and Alexa smart speakers. Yet none of these systems talk to one another or understand **context**. 

When a doorbell rings at 4:08 PM, conventional systems blast a noisy notification: *"Motion detected at Front Door"*. For an older adult with mild cognitive impairment like Arthur (age 78), this creates confusion and anxiety:
- *Who is that?*
- *Why are they here?*
- *Did I forget an appointment?*

Likewise, when Arthur misplaces his reading glasses or forgets to take his morning blood pressure medication, current smart home devices stay silent because they lack memory and behavioral reasoning.

**ContextOS transforms raw sensor noise into contextual understanding, persistent memory, and proactive human assistance.**

---

## 🚀 What ContextOS Does

ContextOS functions as an ambient operating system for the home:
1. **Semantic Memory Graph**: Maintains an active, directional knowledge graph of household entities (Arthur, his neighbor Ravi, daughter Sarah, locations, devices, objects, routines) and relational links (`located_in`, `visited`, `caretaker_of`, `scheduled_at`).
2. **Alexa+ Voice Memory Search**: Arthur can ask natural questions to Alexa:
   - *"Alexa, who is at the door?"* → *"That's your neighbor Ravi. You spoke with him yesterday about tomato plants and expected him today."*
   - *"Alexa, where are my glasses?"* → *"They were last seen on the living room table about 15 minutes ago."*
3. **Omission & Anomaly Engine**: Detects the absence of expected events:
   - Exterior door left open >30 minutes.
   - Late-night door opening (23:00–05:00) flagging dementia wandering risk.
   - Bathroom occupied >45 minutes with no motion, detecting potential falls.
   - Missed morning medication routine windows.
4. **Caregiver Trust Dashboard & Daily Briefing**: Next.js dashboard providing caregivers with:
   - Live SVG interactive memory graph and 2-hop neighborhood context inspector.
   - Daily Autonomy & Safety Score (0–100) and an executive 3-bullet briefing synthesized by Bedrock Claude 3.5 Sonnet.
   - "Why Did You Do That?" CoT drawer showing exact `<thinking>` steps behind every automated alert.
5. **Human-In-The-Loop Safety Gate**: 5-level permission model (`READ`, `SUGGEST`, `CONFIRM`, `ACT`, `ESCALATE`) preventing AI hallucinations from unilaterally executing destructive mutations without confirmation.

---

## 🏗️ Architecture & How We Built It

```text
                  ENVIRONMENTAL SENSORS & INPUTS
              (Ring Doorbell, Motion, Cameras, Door Contacts)
                                   │
                                   ▼
                       RING PERCEPTION ADAPTER
                       (Webhook & State Normalizer)
                                   │
                                   ▼
                        INGESTION & CONTEXT ENGINE
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
          MEMORY GRAPH (SQLAlchemy)       TEMPORAL OMISSION ENGINE
             - Entities (Nodes)             - 60s Heartbeat Sweeper
             - Relationships (Edges)        - Wandering & Fall Rules
             - 2-Hop SQL Traversal          - Scheduled Routine Windows
                    │                             │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
               MODEL CONTEXT PROTOCOL (MCP) SERVER
             [get_entity_context, query_memory_graph, get_recent_events]
                                   │
          ┌────────────────────────┴────────────────────────┐
          ▼                                                 ▼
   ALEXA+ VOICE TURN (<50ms)                      AMAZON BEDROCK CORE
   - Pure deterministic SQL                       - Dual-tier routing
   - Web Speech audio readout                     - Claude 3.5 Haiku (Voice)
   - Zero LLM in hot voice path                   - Claude 3.5 Sonnet (Deep CoT)
                                                            │
                                                            ▼
                                                CAREGIVER TRUST DASHBOARD
                                                - Next.js 14 + Tailwind CSS
                                                - Interactive SVG Graph Canvas
                                                - Real-time SSE Live Ticker
                                                - CoT Reasoning Inspector
                                                - 5-Level Safety Permission Gate
```

### Technical Highlights:
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0 Async (aiosqlite/PostgreSQL), Pydantic v2.
- **AI & Reasoning**: Amazon Bedrock Converse API with Claude 3.5 Sonnet/Haiku and local zero-dependency simulator.
- **Frontend**: Next.js 14 App Router, TypeScript strict mode, Tailwind CSS, Web Speech API speech synthesis.
- **DevOps**: Docker, Docker Compose, and automated GitHub Actions CI pipeline.

---

## 🧪 Verification & Testing

The repository contains 27 comprehensive automated tests covering:
- Graph entity CRUD and 2-hop neighborhood graph traversals.
- Event ingestion and real-time graph state mutations.
- Ring webhook ingestion, threat classification, and device sync.
- Omission detector sweeps (door open, missed medication, wandering, bathroom fall).
- Bedrock `<thinking>` tag isolation and action audit logging.
- 5-level permission barrier (Read, Suggest, Confirm, Act, Escalate).
- Full 3-minute end-to-end hackathon demo pitch scenario.

**All 27 tests pass in < 0.3s.**
