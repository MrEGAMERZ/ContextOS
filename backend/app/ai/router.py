from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.ai.agent import ContextOSAgent
from app.ai.permissions import permission_gate, ActionRequest, PermissionDecision
from app.ai.bedrock_client import bedrock_client
from app.models.audit import ActionAuditLog
from app.schemas.audit import AuditLogRead

router = APIRouter(tags=["Agent & Audit"])

class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language question, e.g. 'Who is at the door?' or 'Where are my glasses?'")

class QueryResponse(BaseModel):
    query: str
    response: str
    thinking_process: str
    audit_id: str
    execution_ms: float
    model_used: str
    grounded_entity: Optional[str] = None

@router.post("/api/agent/query", response_model=QueryResponse)
async def query_agent(
    req: QueryRequest,
    db: AsyncSession = Depends(get_db)
):
    agent = ContextOSAgent(db)
    return await agent.answer_voice_query(req.query)

@router.get("/api/audit/{audit_id}", response_model=AuditLogRead)
async def get_audit_record(
    audit_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ActionAuditLog).where(ActionAuditLog.id == audit_id)
    res = await db.execute(stmt)
    record = res.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail=f"Audit record '{audit_id}' not found")
    return AuditLogRead(
        id=record.id,
        action_type=record.action_type,
        trigger_event_id=record.trigger_event_id,
        prompt_context=record.prompt_context,
        thinking_process=record.thinking_process,
        output_response=record.output_response,
        created_at=record.created_at
    )

@router.get("/api/agent/permissions")
async def get_permission_rules():
    """Returns active permission level policies for smart home actions."""
    return {"policy": permission_gate.get_policy()}

@router.post("/api/agent/actions/evaluate", response_model=PermissionDecision)
async def evaluate_agent_action(action: ActionRequest):
    """Evaluates an AI-proposed action against the 5-level permission policy."""
    return await permission_gate.evaluate_action(action)

@router.get("/api/agent/confirmations/pending")
async def get_pending_confirmations():
    """Returns all actions currently awaiting user/caregiver confirmation."""
    return {"pending_confirmations": permission_gate.get_pending_confirmations()}

class ResolveConfirmationRequest(BaseModel):
    approved: bool = Field(..., description="True to execute the action, False to reject")

@router.post("/api/agent/confirmations/{token}/resolve")
async def resolve_pending_confirmation(token: str, req: ResolveConfirmationRequest):
    """User or caregiver approves/rejects a pending smart-home action."""
    return await permission_gate.resolve_confirmation(token, req.approved)

@router.get("/api/agent/aws-status")
async def check_aws_status():
    """Checks AWS Bedrock IAM credentials and runtime status."""
    return await bedrock_client.verify_aws_credentials()

