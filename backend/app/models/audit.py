import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class ActionAuditLog(Base):
    __tablename__ = "action_audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    trigger_event_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    prompt_context: Mapped[str] = mapped_column(Text, nullable=False)
    thinking_process: Mapped[str] = mapped_column(Text, nullable=False) # Extracted Bedrock <thinking> CoT block
    output_response: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
