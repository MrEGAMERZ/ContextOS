import pytest


@pytest.mark.asyncio
async def test_permission_gate_read_action(async_client):
    # Action under READ policy should execute automatically
    res = await async_client.post("/api/agent/actions/evaluate", json={
        "action_type": "query_memory_graph",
        "target_entity": "Arthur",
        "parameters": {"query": "Where are my glasses?"}
    })
    assert res.status_code == 200
    data = res.json()
    assert data["allowed"] is True
    assert data["status"] == "EXECUTED"
    assert data["required_level"] == "read"


@pytest.mark.asyncio
async def test_permission_gate_confirm_action_workflow(async_client):
    # 1. Action under CONFIRM policy must halt and produce confirmation token
    res = await async_client.post("/api/agent/actions/evaluate", json={
        "action_type": "lock_door",
        "target_entity": "Front Door",
        "parameters": {"door": "Front Door", "state": "lock"},
        "reasoning": "Front door left open >30 minutes"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["allowed"] is False
    assert data["status"] == "PENDING_CONFIRMATION"
    assert data["required_level"] == "confirm"
    token = data["confirmation_token"]
    assert token is not None

    # 2. Verify token is in pending confirmations
    pending_res = await async_client.get("/api/agent/confirmations/pending")
    assert pending_res.status_code == 200
    pending_list = pending_res.json()["pending_confirmations"]
    assert any(c["confirmation_token"] == token for c in pending_list)

    # 3. Approve confirmation
    resolve_res = await async_client.post(
        f"/api/agent/confirmations/{token}/resolve",
        json={"approved": True}
    )
    assert resolve_res.status_code == 200
    resolve_data = resolve_res.json()
    assert resolve_data["status"] == "success"
    assert resolve_data["decision"] == "approved"
    assert resolve_data["executed"] is True

    # 4. Confirm it is no longer pending
    pending_res2 = await async_client.get("/api/agent/confirmations/pending")
    assert not any(c["confirmation_token"] == token for c in pending_res2.json()["pending_confirmations"])


@pytest.mark.asyncio
async def test_permission_gate_escalate_action(async_client):
    # Action under ESCALATE policy must dispatch critical caregiver alert
    res = await async_client.post("/api/agent/actions/evaluate", json={
        "action_type": "notify_emergency_contact",
        "target_entity": "Sarah",
        "parameters": {"severity": "critical", "reason": "Late night wandering detected"},
        "reasoning": "Exterior door opened at 2:30 AM"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["allowed"] is True
    assert data["status"] == "ESCALATED"
    assert data["required_level"] == "escalate"


@pytest.mark.asyncio
async def test_aws_status_and_permissions_policy(async_client):
    # Policy listing
    perm_res = await async_client.get("/api/agent/permissions")
    assert perm_res.status_code == 200
    policy = perm_res.json()["policy"]
    assert policy.get("lock_door") == "confirm"
    assert policy.get("query_memory_graph") == "read"
    assert policy.get("notify_emergency_contact") == "escalate"

    # AWS status
    aws_res = await async_client.get("/api/agent/aws-status")
    assert aws_res.status_code == 200
    aws_data = aws_res.json()
    assert "status" in aws_data
    assert "region" in aws_data
    assert "fast_model_id" in aws_data
    assert "deep_model_id" in aws_data
