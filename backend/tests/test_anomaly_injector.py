import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from app.repository.graph_repo import GraphRepository
from app.schemas.graph import EntityCreate
from app.engine.stream import broadcaster

@pytest.mark.asyncio
async def test_inject_visitor_arrival(async_client, test_session):
    repo = GraphRepository(test_session)
    await repo.create_entity(EntityCreate(name="Arthur", entity_type="person"))
    await repo.create_entity(EntityCreate(name="Front Porch", entity_type="location"))

    resp = await async_client.post("/api/events/inject", json={
        "scenario": "visitor_arrival"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["scenario"] == "visitor_arrival"
    assert data["ingest_result"]["status"] == "success"

    # Verify Ravi entity exists
    ravi = await repo.get_entity_by_name("Ravi")
    assert ravi is not None
    assert ravi.metadata_["last_location"] == "Front Porch"

@pytest.mark.asyncio
async def test_door_open_anomaly_omission(async_client, test_session):
    repo = GraphRepository(test_session)
    # Create door entity
    await repo.create_entity(EntityCreate(name="Front Porch", entity_type="location", metadata={"state": "closed"}))

    # Trigger front_door_open_anomaly scenario
    resp = await async_client.post("/api/events/inject", json={
        "scenario": "front_door_open_anomaly"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["anomalies_detected"]) >= 1
    anomaly = data["anomalies_detected"][0]
    assert anomaly["type"] == "door_open_omission"
    assert "Door Left Open" in anomaly["title"]
    assert "State Evaluation" in anomaly["thinking_process"]
    assert anomaly["audit_id"] is not None

@pytest.mark.asyncio
async def test_missed_medication_omission(async_client, test_session):
    repo = GraphRepository(test_session)
    await repo.create_entity(EntityCreate(
        name="Morning Medication Routine",
        entity_type="routine",
        metadata={"window_end": "09:30"}
    ))

    resp = await async_client.post("/api/events/inject", json={
        "scenario": "missed_medication"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["anomalies_detected"]) >= 1
    anomaly = data["anomalies_detected"][0]
    assert anomaly["type"] == "routine_missed_omission"

@pytest.mark.asyncio
async def test_sse_broadcaster():
    q = broadcaster.subscribe()
    await broadcaster.broadcast({"test": "message"})
    msg = await asyncio.wait_for(q.get(), timeout=1.0)
    assert msg["test"] == "message"
    broadcaster.unsubscribe(q)
