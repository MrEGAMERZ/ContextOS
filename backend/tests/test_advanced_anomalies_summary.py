import pytest


@pytest.mark.asyncio
async def test_wandering_nighttime_anomaly(async_client):
    # Trigger wandering_nighttime scenario
    res = await async_client.post("/api/events/inject", json={"scenario": "wandering_nighttime"})
    assert res.status_code == 200
    data = res.json()
    assert data["scenario"] == "wandering_nighttime"
    anomalies = data["anomalies_detected"]
    assert len(anomalies) >= 1
    wandering = next((a for a in anomalies if a["type"] == "wandering_alert"), None)
    assert wandering is not None
    assert "Wandering" in wandering["title"] or "Wandering" in wandering["description"]
    assert wandering["audit_id"] is not None


@pytest.mark.asyncio
async def test_extended_bathroom_inactivity_fall_risk(async_client):
    # Trigger bathroom_fall scenario
    res = await async_client.post("/api/events/inject", json={"scenario": "bathroom_fall"})
    assert res.status_code == 200
    data = res.json()
    assert data["scenario"] == "bathroom_fall"
    anomalies = data["anomalies_detected"]
    assert len(anomalies) >= 1
    fall_alert = next((a for a in anomalies if a["type"] == "fall_risk_alert"), None)
    assert fall_alert is not None
    assert "Bathroom" in fall_alert["description"]
    assert "Fall" in fall_alert["title"]


@pytest.mark.asyncio
async def test_caregiver_health_metrics_and_briefing(async_client):
    # Ingest a social event first
    await async_client.post("/api/ring/simulate", json={"scenario": "ding_neighbor"})

    # 1. Health score endpoint
    score_res = await async_client.get("/api/caregiver/health-score")
    assert score_res.status_code == 200
    metrics = score_res.json()
    assert 0 <= metrics["autonomy_score"] <= 100
    assert metrics["status_label"] in ("Excellent", "Stable", "Attention Needed", "Critical")
    assert "medication_adherence_percent" in metrics
    assert metrics["social_interactions_count"] >= 1

    # 2. Daily briefing endpoint
    briefing_res = await async_client.get("/api/caregiver/briefing")
    assert briefing_res.status_code == 200
    briefing = briefing_res.json()
    assert briefing["target_person"] == "Arthur"
    assert len(briefing["summary_bullets"]) >= 1
    assert len(briefing["action_items"]) >= 1
    assert "claude" in briefing["bedrock_model_used"].lower()


@pytest.mark.asyncio
async def test_caregiver_briefing_force_generate(async_client):
    res = await async_client.post("/api/caregiver/briefing/generate")
    assert res.status_code == 200
    data = res.json()
    assert "autonomy_score" in data
    assert "summary_bullets" in data
    assert len(data["summary_bullets"]) >= 1
