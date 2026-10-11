import pytest
from app.repository.graph_repo import GraphRepository
from app.schemas.graph import EntityCreate, RelationshipCreate

@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ContextOS"

@pytest.mark.asyncio
async def test_entity_crud_and_neighborhood(test_session):
    repo = GraphRepository(test_session)

    # 1. Create entities
    arthur = await repo.create_entity(EntityCreate(
        name="Arthur",
        entity_type="person",
        metadata={"age": 78}
    ))
    assert arthur.id is not None
    assert arthur.name == "Arthur"

    living_room = await repo.create_entity(EntityCreate(
        name="Living Room",
        entity_type="location",
        metadata={"floor": 1}
    ))

    glasses = await repo.create_entity(EntityCreate(
        name="Reading Glasses",
        entity_type="object",
        metadata={"confidence": 0.95}
    ))

    # 2. Add relationships
    # Arthur in Living Room
    rel1 = await repo.add_relationship(RelationshipCreate(
        source_entity_id=arthur.id,
        target_entity_id=living_room.id,
        relation_type="located_in",
        weight=1.0
    ))
    assert rel1.id is not None

    # Glasses in Living Room
    rel2 = await repo.add_relationship(RelationshipCreate(
        source_entity_id=glasses.id,
        target_entity_id=living_room.id,
        relation_type="located_in",
        weight=0.9
    ))
    assert rel2.id is not None

    # 3. Query 2-hop neighborhood of Arthur
    # Hop 1: Living Room
    # Hop 2: Reading Glasses (via Living Room)
    neighborhood = await repo.get_entity_neighborhood("Arthur")
    assert neighborhood is not None
    assert neighborhood.center.name == "Arthur"
    assert len(neighborhood.immediate_neighbors) == 1
    assert neighborhood.immediate_neighbors[0].entity.name == "Living Room"

    # 2-hop neighbor should contain Reading Glasses
    two_hop_names = [n.entity.name for n in neighborhood.two_hop_neighbors]
    assert "Reading Glasses" in two_hop_names

@pytest.mark.asyncio
async def test_event_and_audit_logging(test_session):
    repo = GraphRepository(test_session)

    # 1. Create event
    event = await repo.create_event(
        event_type="doorbell_rung",
        source_device="ring_front_door",
        payload={"visitor": "Ravi", "confidence": 0.96}
    )
    assert event.id is not None
    assert event.event_type == "doorbell_rung"

    # 2. Query recent events
    recent = await repo.list_recent_events(limit=5)
    assert len(recent) == 1
    assert recent[0].payload["visitor"] == "Ravi"

    # 3. Create action audit log
    audit = await repo.log_action(
        action_type="alexa_voice_response",
        prompt_context="Who is at the front door?",
        thinking_process="<thinking>The visitor detected is Ravi, neighbor with high confidence.</thinking>",
        output_response="That's your neighbor Ravi. He was expected today.",
        trigger_event_id=event.id
    )
    assert audit.id is not None
    assert "<thinking>" in audit.thinking_process

    # 4. Query audit logs
    audit_logs = await repo.list_audit_logs(limit=5)
    assert len(audit_logs) == 1
    assert audit_logs[0].action_type == "alexa_voice_response"

@pytest.mark.asyncio
async def test_api_graph_endpoints(async_client):
    # Test creating entity via API
    resp = await async_client.post("/api/graph/entities", json={
        "name": "Sarah",
        "entity_type": "person",
        "metadata": {"role": "daughter"}
    })
    assert resp.status_code == 201
    entity_data = resp.json()
    assert entity_data["name"] == "Sarah"

    # Test listing entities
    list_resp = await async_client.get("/api/graph/entities")
    assert list_resp.status_code == 200
    names = [e["name"] for e in list_resp.json()]
    assert "Sarah" in names
