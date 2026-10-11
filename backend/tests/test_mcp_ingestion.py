import pytest
from app.repository.graph_repo import GraphRepository
from app.schemas.graph import EntityCreate, RelationshipCreate

@pytest.mark.asyncio
async def test_event_ingestion_mutates_graph(async_client, test_session):
    repo = GraphRepository(test_session)
    
    # 1. Seed Arthur and Front Porch
    arthur = await repo.create_entity(EntityCreate(name="Arthur", entity_type="person"))
    front_porch = await repo.create_entity(EntityCreate(name="Front Porch", entity_type="location"))
    living_room = await repo.create_entity(EntityCreate(name="Living Room", entity_type="location"))

    # 2. Ingest doorbell ring event with visitor Ravi
    ingest_resp = await async_client.post("/api/events/ingest", json={
        "event_type": "doorbell_rung",
        "source_device": "ring_front_door",
        "payload": {
            "visitor": "Ravi",
            "location": "Front Porch",
            "confidence": 0.98
        }
    })
    assert ingest_resp.status_code == 201
    data = ingest_resp.json()
    assert data["status"] == "success"
    assert "relationship_updated" in data["graph_updates"]

    # Verify Ravi entity was automatically created and updated
    ravi = await repo.get_entity_by_name("Ravi")
    assert ravi is not None
    assert ravi.metadata_["last_location"] == "Front Porch"

    # 3. Ingest object moved event
    obj_resp = await async_client.post("/api/events/ingest", json={
        "event_type": "object_moved",
        "source_device": "living_room_cam",
        "payload": {
            "object": "Reading Glasses",
            "location": "Living Room",
            "confidence": 0.95
        }
    })
    assert obj_resp.status_code == 201
    obj_data = obj_resp.json()
    assert "relationship_updated" in obj_data["graph_updates"]

    glasses = await repo.get_entity_by_name("Reading Glasses")
    assert glasses is not None
    assert glasses.metadata_["last_seen_location"] == "Living Room"

@pytest.mark.asyncio
async def test_mcp_tools_and_voice_sla(async_client, test_session):
    repo = GraphRepository(test_session)
    arthur = await repo.create_entity(EntityCreate(name="Arthur", entity_type="person", metadata={"role": "owner"}))
    glasses = await repo.create_entity(EntityCreate(name="Reading Glasses", entity_type="object", metadata={"last_seen_location": "Living Room"}))
    living_room = await repo.create_entity(EntityCreate(name="Living Room", entity_type="location"))

    await repo.add_relationship(RelationshipCreate(
        source_entity_id=glasses.id,
        target_entity_id=living_room.id,
        relation_type="located_in",
        weight=0.95
    ))

    # 1. Test tools list
    tools_resp = await async_client.get("/api/mcp/tools")
    assert tools_resp.status_code == 200
    tools = tools_resp.json()["tools"]
    tool_names = [t["name"] for t in tools]
    assert "get_entity_context" in tool_names
    assert "get_recent_events" in tool_names
    assert "query_memory_graph" in tool_names

    # 2. Test get_entity_context execution SLA
    call_resp = await async_client.post("/api/mcp/call", json={
        "tool": "get_entity_context",
        "arguments": {"entity_name": "Reading Glasses"}
    })
    assert call_resp.status_code == 200
    res_data = call_resp.json()
    assert res_data["tool"] == "get_entity_context"
    assert res_data["data"]["found"] is True
    assert res_data["execution_ms"] < 50.0 # Voice turn SLA guarantee
    assert res_data["sla_pass"] is True

    # 3. Test query_memory_graph
    query_resp = await async_client.post("/api/mcp/call", json={
        "tool": "query_memory_graph",
        "arguments": {"query": "glasses"}
    })
    assert query_resp.status_code == 200
    q_data = query_resp.json()
    assert q_data["data"]["results_count"] >= 1
    assert q_data["execution_ms"] < 50.0

@pytest.mark.asyncio
async def test_mcp_jsonrpc_protocol(async_client):
    # Test initialize
    init_resp = await async_client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    })
    assert init_resp.status_code == 200
    assert init_resp.json()["result"]["serverInfo"]["name"] == "ContextOS-MCP"

    # Test tools/list
    list_resp = await async_client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    })
    assert list_resp.status_code == 200
    assert len(list_resp.json()["result"]["tools"]) == 3

    # Test ping
    ping_resp = await async_client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 3,
        "method": "ping"
    })
    assert ping_resp.status_code == 200
    assert ping_resp.json()["result"] == {}
