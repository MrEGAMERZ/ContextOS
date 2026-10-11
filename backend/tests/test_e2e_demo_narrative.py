import pytest
from app.seed import seed_household_graph
from app.repository.graph_repo import GraphRepository

@pytest.mark.asyncio
async def test_complete_hackathon_demo_narrative(async_client, test_session):
    """
    End-to-End Integration Test for the complete 3-minute Hackathon Pitch Demo:
    1. Seed household graph
    2. Ring doorbell event -> Graph update
    3. Alexa voice turn -> Neighbor recognition with garden context
    4. Object recall query -> Glasses location
    5. Omission anomaly -> Door open 35m -> Bedrock CoT audit log
    6. Caregiver Trust Dashboard serving verification
    """
    # Step 1: Seed Household Graph in test session
    repo = GraphRepository(test_session)
    from app.schemas.graph import EntityCreate, RelationshipCreate
    arthur = await repo.create_entity(EntityCreate(name="Arthur", entity_type="person", metadata={"age": 78}))
    front_porch = await repo.create_entity(EntityCreate(name="Front Porch", entity_type="location"))
    living_room = await repo.create_entity(EntityCreate(name="Living Room", entity_type="location"))
    glasses = await repo.create_entity(EntityCreate(name="Reading Glasses", entity_type="object", metadata={"last_seen_location": "Living Room Table"}))
    await repo.add_relationship(RelationshipCreate(source_entity_id=glasses.id, target_entity_id=living_room.id, relation_type="located_in"))

    # Step 2: Inject Event — Ring Doorbell detects Ravi
    inj_resp = await async_client.post("/api/events/inject", json={"scenario": "visitor_arrival"})
    assert inj_resp.status_code == 200
    assert inj_resp.json()["scenario"] == "visitor_arrival"

    # Step 3: Alexa+ Voice Query — "Who is at the front door?"
    query_resp1 = await async_client.post("/api/agent/query", json={"query": "Who is at the front door?"})
    assert query_resp1.status_code == 200
    ans1 = query_resp1.json()
    assert "Ravi" in ans1["response"]
    assert ans1["execution_ms"] > 0
    assert ans1["audit_id"] is not None

    # Step 4: Alexa+ Voice Query — "Where are my glasses?"
    query_resp2 = await async_client.post("/api/agent/query", json={"query": "Where are my glasses?"})
    assert query_resp2.status_code == 200
    ans2 = query_resp2.json()
    assert "glasses" in ans2["response"].lower() or "table" in ans2["response"].lower()

    # Step 5: Omission Detection — Door left open for 35 minutes
    inj_anomaly = await async_client.post("/api/events/inject", json={"scenario": "front_door_open_anomaly"})
    assert inj_anomaly.status_code == 200
    anomaly_data = inj_anomaly.json()
    assert len(anomaly_data["anomalies_detected"]) >= 1
    anomaly = anomaly_data["anomalies_detected"][0]
    assert anomaly["type"] == "door_open_omission"
    assert "State Evaluation" in anomaly["thinking_process"]
    assert anomaly["audit_id"] is not None

    # Step 6: Verify "Why Did You Do That?" Audit Drawer Endpoint
    audit_resp = await async_client.get(f"/api/audit/{anomaly['audit_id']}")
    assert audit_resp.status_code == 200
    audit_data = audit_resp.json()
    assert "State Evaluation" in audit_data["thinking_process"]

    # Step 7: Verify Caregiver Dashboard UI is served
    dash_resp = await async_client.get("/dashboard")
    assert dash_resp.status_code == 200
    assert "ContextOS" in dash_resp.text
    assert "Semantic Memory Graph" in dash_resp.text
