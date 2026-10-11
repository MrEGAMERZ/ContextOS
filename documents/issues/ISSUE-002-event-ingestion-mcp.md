# Issue #2: Event Ingestion Pipeline & Alexa+ MCP Server

**Status:** Queued  
**Shipment:** Shipment 2  
**Labels:** `mcp`, `alexa`, `ingestion`, `shipment-2`

## Description
Implement the event ingestion engine that normalizes raw smart home events into relational graph updates, and build the Model Context Protocol (MCP) server supporting Streamable HTTP / Server-Sent Events (SSE). Expose high-speed (<50ms) MCP tools that Alexa+ or a voice assistant can call to query the home's context without violating the 8-second voice SLA.

## Acceptance Criteria
1. FastAPI endpoint `POST /api/events/ingest` to ingest and normalize smart home events.
2. Automatic graph mutation:
   - Door open/close events update entity states.
   - Sighting events create or update `located_in` / `associated_with` edges.
3. Self-Hosted MCP Server implementation over HTTP / SSE transport:
   - `get_entity_context(entity_name: str) -> dict`: 2-hop neighborhood of requested entity.
   - `get_recent_events(limit: int = 10, event_type: Optional[str] = None) -> list`: Chronological recent events.
   - `query_memory_graph(query: str) -> dict`: Fast semantic / indexed search over graph entities.
4. Execution SLA: All 3 MCP tools must resolve in <50ms (deterministic database queries; zero nested LLM calls).
5. Comprehensive test suite with mocked MCP protocol handshake and tool execution.
