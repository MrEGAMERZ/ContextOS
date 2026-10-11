from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class AuditLogBase(BaseModel):
    action_type: str = Field(..., description="Action category, e.g. alexa_voice_response, proactive_insight, caregiver_escalation")
    trigger_event_id: Optional[str] = None
    prompt_context: str
    thinking_process: str
    output_response: str

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogRead(AuditLogBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
