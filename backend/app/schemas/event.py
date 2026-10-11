from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Dict, Any, Optional

class EventBase(BaseModel):
    event_type: str = Field(..., description="Type of event, e.g. doorbell_rung, person_detected, motion_detected")
    source_device: str = Field(..., description="Source device ID or name, e.g. ring_front_door")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary event payload (person name, confidence, etc)")

class EventCreate(EventBase):
    occurred_at: Optional[datetime] = None

class EventRead(EventBase):
    id: str
    occurred_at: datetime

    model_config = ConfigDict(from_attributes=True)

class IngestEventResponse(BaseModel):
    status: str
    event: EventRead
    graph_updates: Dict[str, Any] = Field(default_factory=dict)
    immediate_alerts: list = Field(default_factory=list)
