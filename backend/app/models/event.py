import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True) # doorbell_rung, person_detected, motion_detected, query_asked, omission_detected
    source_device: Mapped[str] = mapped_column(String(128), nullable=False, index=True) # ring_doorbell, alexa_living_room, etc.
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
