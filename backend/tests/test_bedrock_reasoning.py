import pytest
from app.ai.bedrock_client import BedrockClient
from app.ai.agent import ContextOSAgent
from app.repository.graph_repo import GraphRepository
from app.schemas.graph import EntityCreate, RelationshipCreate

def test_thinking_tag_extraction():
    raw_with_thinking = (
        "<thinking>\n"
        "1. Identify entity: Ravi.\n"
        "2. Neighbor relationship confirmed.\n"
        "</thinking>\n"
        "That's your neighbor Ravi. He is visiting about the garden."
    )
    thinking, response = BedrockClient.extract_thinking_and_response(raw_with_thinking)
    assert "1. Identify entity: Ravi" in thinking
    assert "That's your neighbor Ravi" in response
    assert "<thinking>" not in response

    # Raw without thinking
    raw_no_thinking = "Your glasses are on the table."
    thinking_fallback, response2 = BedrockClient.extract_thinking_and_response(raw_no_thinking)
    assert response2 == "Your glasses are on the table."
    assert "Direct inference" in thinking_fallback

@pytest.mark.asyncio
async def test_agent_voice_query_and_audit_trail(async_client, test_session):
    repo = GraphRepository(test_session)
    # Seed Ravi
    ravi = await repo.create_entity(EntityCreate(
        name="Ravi",
        entity_type="person",
        metadata={"role": "neighbor", "notes": "Spoke yesterday about garden."}
    ))

    # Ask conversational query
    resp = await async_client.post("/api/agent/query", json={
        "query": "Who is at the front door?"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "Ravi" in data["response"]
    assert "Entity Resolution" in data["thinking_process"]
    assert data["audit_id"] is not None
    assert data["execution_ms"] > 0

    # Retrieve audit log record for "Why Did You Do That?" drawer
    audit_resp = await async_client.get(f"/api/audit/{data['audit_id']}")
    assert audit_resp.status_code == 200
    audit_data = audit_resp.json()
    assert audit_data["action_type"] == "alexa_voice_turn"
    assert "Entity Resolution" in audit_data["thinking_process"]
    assert "Ravi" in audit_data["output_response"]

@pytest.mark.asyncio
async def test_deep_reasoning_pipeline(test_session):
    agent = ContextOSAgent(test_session)
    result = await agent.deep_reasoning_inference(
        event_id=None,
        topic="Front door left open for 31 minutes",
        context_subgraph={"door": "Front Porch", "state": "open", "duration_minutes": 31}
    )
    assert result["audit_id"] is not None
    assert "State Evaluation" in result["thinking_process"]
    assert "door has been left open" in result["analysis"].lower()
