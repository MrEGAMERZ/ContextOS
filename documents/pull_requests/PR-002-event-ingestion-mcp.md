# PR #2: Event Ingestion Pipeline & Alexa+ MCP Server

**Branch:** `feat/shipment-2-mcp-ingestion` -> `main`  
**Shipment:** Shipment 2 (`v0.2.0-shipment2`)  
**Status:** Merged  
**Related Issue:** #2 ([documents/issues/ISSUE-002-event-ingestion-mcp.md](../issues/ISSUE-002-event-ingestion-mcp.md))

## Summary
Implements the real-time event ingestion engine that normalizes smart home events and mutates the memory graph, plus the Model Context Protocol (MCP) server supporting Streamable HTTP and JSON-RPC 2.0 with sub-50ms tool execution for Alexa+ voice turns.

## Changes
- **Event Ingestion Engine (`backend/app/engine/ingestion.py`)**:
  - Ingestion of raw normalized events (`doorbell_rung`, `person_detected`, `object_detected`, `door_opened`, `routine_completed`).
  - Automatic graph mutation: updates entity attributes (`last_seen`, `last_location`, `state`), discovers new visitors, creates/updates `visited` and `located_in` edges.
- **MCP Server & Tool Handlers (`backend/app/mcp/server.py`)**:
  - Implements 3 high-speed MCP tools:
    1. `get_entity_context`: 2-hop neighborhood, relations, and recent observations.
    2. `get_recent_events`: Chronological stream of sensory events.
    3. `query_memory_graph`: Semantic keyword lookup across entities and active states.
  - Strict Voice SLA Guarantee: All tools resolve in <50ms using deterministic SQL lookups (zero nested LLM latency).
- **Protocol Routers (`backend/app/mcp/router.py`, `backend/app/engine/router.py`)**:
  - `POST /api/events/ingest`: Real-time sensory event ingestion.
  - `POST /mcp`: Standard MCP JSON-RPC 2.0 handler (`initialize`, `tools/list`, `tools/call`, `ping`).
  - `POST /api/mcp/call`: Fast REST tool calling interface.
  - `GET /api/mcp/tools`: Tool schema registry.
- **Pytest Suite (`backend/tests/test_mcp_ingestion.py`)**:
  - Automated verification of event ingestion graph mutations, MCP tool SLA compliance, and JSON-RPC protocol handshakes.

## Test Verification
- All 7 tests pass in `0.10s`.
- MCP tools execute within `<1.5ms`, far surpassing the `<50ms` SLA requirement.
