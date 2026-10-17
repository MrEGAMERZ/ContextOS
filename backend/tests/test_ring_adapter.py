import pytest
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_ring_webhook_ding_neighbor(async_client):
    payload = {
        "event_id": "ring_ding_test_001",
        "kind": "ding",
        "device_id": "ring_doorbell_pro_front",
        "device_name": "Front Door Video Doorbell",
        "location": "Front Porch",
        "person_detected": True,
        "person_name": "Ravi",
        "confidence": 0.98,
        "battery_level": 94
    }
    res = await async_client.post("/api/ring/webhook", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["normalized_event_type"] == "doorbell_rung"
    assert data["threat_level"] == "LOW"
    assert "Ravi" in data["context_summary"]
    assert data["device_synced"] == "Front Door Video Doorbell"


@pytest.mark.asyncio
async def test_ring_webhook_late_night_motion(async_client):
    night_time = datetime(2026, 10, 17, 2, 30, tzinfo=timezone.utc)
    payload = {
        "event_id": "ring_motion_test_002",
        "kind": "person_detected",
        "device_id": "ring_doorbell_pro_front",
        "device_name": "Front Door Video Doorbell",
        "location": "Front Porch",
        "person_detected": True,
        "person_name": "Unknown Individual",
        "confidence": 0.89,
        "occurred_at": night_time.isoformat()
    }
    res = await async_client.post("/api/ring/webhook", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["normalized_event_type"] == "person_detected"
    assert data["threat_level"] == "HIGH"
    assert "Security Alert" in data["context_summary"] or "late hours" in data["context_summary"]


@pytest.mark.asyncio
async def test_ring_simulate_endpoint(async_client):
    res = await async_client.post("/api/ring/simulate", json={"scenario": "ding_stranger"})
    assert res.status_code == 200
    data = res.json()
    assert data["normalized_event_type"] == "doorbell_rung"
    assert data["threat_level"] == "MEDIUM"
    assert "Unknown visitor" in data["context_summary"]


@pytest.mark.asyncio
async def test_ring_devices_and_recent_endpoints(async_client):
    # Trigger an event first
    await async_client.post("/api/ring/simulate", json={"scenario": "motion_package"})

    # Verify device listing
    dev_res = await async_client.get("/api/ring/devices")
    assert dev_res.status_code == 200
    devices = dev_res.json()["ring_devices"]
    assert len(devices) >= 1
    assert any("Doorbell" in d["name"] for d in devices)

    # Verify recent events
    rec_res = await async_client.get("/api/ring/recent?limit=5")
    assert rec_res.status_code == 200
    events = rec_res.json()["events"]
    assert len(events) >= 1
    assert events[0]["source_device"] == "Front Door Video Doorbell"
