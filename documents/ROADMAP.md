# ContextOS — Hackathon Execution Roadmap & Shipment Tracking

## Overview
ContextOS is an ambient, context-aware AI assistance platform designed to understand human environments, relationships, routines, objects, and events, turning raw sensor noise into contextual understanding and proactive assistance.

**Hackathon Track:** Alexa+ (Self-Hosted Model Context Protocol Server) & Ring (Perception/Event Ingestion)  
**Mini-Challenge:** AWS Builder (Bedrock Claude 3.5 Sonnet/Haiku dual-tier reasoning with `<thinking>` Chain of Thought)

---

## 5-Shipment Execution Plan

| Shipment | Scope | Target Tag | Status | PR |
|---|---|---|---|---|
| **Shipment 1** | **Memory Graph Engine & Database Foundation** (Entities, Relationships, Events, Audit Logs, SQLite/PostgreSQL Dual Engine) | `v0.1.0-shipment1` | Completed | PR #1 |
| **Shipment 2** | **Event Ingestion Pipeline & Alexa+ MCP Server** (Streamable HTTP / SSE MCP Protocol, 3 High-Speed Voice Tools) | `v0.2.0-shipment2` | Completed | PR #2 |
| **Shipment 3** | **Dual-Tier Bedrock Agent & Chain-of-Thought Engine** (Claude 3.5 Haiku/Sonnet, `<thinking>` Tag Extraction, Action Audit Logging) | `v0.3.0-shipment3` | Completed | PR #3 |
| **Shipment 4** | **Anomaly & Omission Engine + Simulated Event Injector** (60s Temporal Clock, Routine Checking, Demo Scenarios) | `v0.4.0-shipment4` | Completed | PR #4 |
| **Shipment 5** | **Caregiver Trust Dashboard & Voice Simulator** (Next.js UI, React Flow Graph, Live CoT Viewer, Alexa+ Voice Testbed) | `v0.5.0-shipment5` | Queued | PR #5 |

---

## Daily Shipment Log
- **2026-10-11**:
  - Issue #1 / PR #1: Scaffold Backend, Database Models, Graph Repository, Seed Data & Pytest Suite.
  - Issue #2 / PR #2: Ingestion Pipeline & Streamable HTTP / SSE MCP Tools (`get_entity_context`, `get_recent_events`, `query_memory_graph`).
  - Issue #3 / PR #3: Bedrock Dual-Tier Agent with `<thinking>` Chain-of-Thought Extractor & Audit Trail.
  - Issue #4 / PR #4: Temporal Omission Worker & Synthetic Event Injector presets.
  - Issue #5 / PR #5: Caregiver Trust UI, Graph Visualizer, CoT Inspector & Alexa Voice Harness.
