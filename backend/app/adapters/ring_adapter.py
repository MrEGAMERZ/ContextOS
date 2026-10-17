"""Ring Doorbell and Camera Perception Adapter for ContextOS.

Translates raw Ring webhooks (ding, motion, person_detected, live view)
into canonical ContextOS memory graph events and contextual interpretations.
Supports both real Ring Webhooks (OAuth/HMAC signature) and Simulated Ring Harness for demos.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.event import EventCreate, IngestEventResponse
from app.schemas.graph import EntityCreate, RelationshipCreate
from app.repository.graph_repo import GraphRepository
from app.engine.ingestion import IngestionEngine
from app.engine.stream import broadcaster


class RingWebhookPayload(BaseModel):
    event_id: str = Field(default_factory=lambda: f"ring_evt_{int(datetime.now(timezone.utc).timestamp())}")
    kind: str = Field(..., description="ding, motion, person_detected, on_demand, door_activity")
    device_id: str = Field(default="ring_front_door_01")
    device_name: str = Field(default="Front Door Video Doorbell")
    location: str = Field(default="Front Porch")
    person_detected: bool = Field(default=False)
    person_name: Optional[str] = Field(default=None)
    confidence: float = Field(default=0.92)
    snapshot_url: Optional[str] = Field(default="https://assets.contextos.internal/ring/snapshot_front_door.jpg")
    video_clip_url: Optional[str] = Field(default="https://assets.contextos.internal/ring/clip_front_door.mp4")
    battery_level: Optional[int] = Field(default=88)
    signal_rssi: Optional[int] = Field(default=-58)
    occurred_at: Optional[datetime] = Field(default=None)


class RingSimulationRequest(BaseModel):
    scenario: str = Field(..., description="'ding_neighbor', 'ding_stranger', 'motion_package', 'late_night_motion'")
    person_name: Optional[str] = None
    device_name: Optional[str] = "Front Door Video Doorbell"


class RingEventResult(BaseModel):
    ring_event_id: str
    normalized_event_type: str
    context_summary: str
    threat_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    device_synced: str
    graph_mutations: Dict[str, Any]
    persisted_event_id: str


class RingAdapter:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = GraphRepository(session)
        self.engine = IngestionEngine(session)

    async def sync_ring_device_entity(self, device_id: str, device_name: str, location: str, battery: Optional[int]) -> Any:
        """Ensures the Ring device is registered as an Entity and linked to its physical location."""
        device_entity = await self.repo.get_entity_by_name(device_name)
        now_iso = datetime.now(timezone.utc).isoformat()
        
        if not device_entity:
            device_entity = await self.repo.create_entity(EntityCreate(
                name=device_name,
                entity_type="device",
                metadata={
                    "hardware_type": "ring_doorbell",
                    "device_id": device_id,
                    "location": location,
                    "battery_level": battery or 100,
                    "last_ping": now_iso
                }
            ))
        else:
            meta = dict(device_entity.metadata_ or {})
            meta["battery_level"] = battery or meta.get("battery_level", 100)
            meta["last_ping"] = now_iso
            device_entity.metadata_ = meta
            device_entity.updated_at = datetime.now(timezone.utc)
            await self.session.commit()

        # Connect device to location if location exists
        loc_entity = await self.repo.get_entity_by_name(location)
        if loc_entity:
            try:
                await self.repo.add_relationship(RelationshipCreate(
                    source_entity_id=device_entity.id,
                    target_entity_id=loc_entity.id,
                    relation_type="located_in",
                    weight=1.0,
                    metadata={"hardware": "ring"}
                ))
            except Exception:
                pass  # Relationship might already exist
        
        return device_entity

    async def process_ring_webhook(self, payload: RingWebhookPayload) -> RingEventResult:
        """Transforms a Ring webhook payload into a canonical ContextOS memory graph event."""
        occurred_at = payload.occurred_at or datetime.now(timezone.utc)
        
        # 1. Sync Ring device in graph
        device_entity = await self.sync_ring_device_entity(
            device_id=payload.device_id,
            device_name=payload.device_name,
            location=payload.location,
            battery=payload.battery_level
        )

        # 2. Determine canonical ContextOS event type & context
        kind = payload.kind.lower()
        threat_level = "LOW"
        context_summary = ""
        event_payload: Dict[str, Any] = {
            "source_hardware": "Ring",
            "ring_event_id": payload.event_id,
            "device_id": payload.device_id,
            "location": payload.location,
            "snapshot_url": payload.snapshot_url,
            "video_clip_url": payload.video_clip_url,
            "confidence": payload.confidence,
        }

        if kind == "ding":
            event_type = "doorbell_rung"
            person = payload.person_name or "Unknown Visitor"
            event_payload["visitor"] = person
            
            # Contextual inquiry in graph
            person_entity = await self.repo.get_entity_by_name(person)
            if person_entity and person_entity.metadata_.get("relationship") == "neighbor":
                context_summary = f"Ring Doorbell: Neighbor {person} pressed the chime at {payload.location}. Known visitor."
                threat_level = "LOW"
            elif person == "Unknown Visitor":
                context_summary = f"Ring Doorbell: Unknown visitor pressed the chime at {payload.location}."
                threat_level = "MEDIUM"
            else:
                context_summary = f"Ring Doorbell: {person} pressed the chime at {payload.location}."
                threat_level = "LOW"

        elif kind in ("person_detected", "motion") and payload.person_detected:
            event_type = "person_detected"
            person = payload.person_name or "Unidentified Individual"
            event_payload["person"] = person
            
            # Check for late night motion
            hour = occurred_at.hour
            if hour >= 23 or hour < 5:
                threat_level = "HIGH"
                context_summary = f"Ring Security Alert: Person motion detected at {payload.location} during late hours ({occurred_at.strftime('%H:%M')})."
            else:
                threat_level = "LOW"
                context_summary = f"Ring Perception: {person} detected approaching {payload.location} ({int(payload.confidence * 100)}% confidence)."

        elif kind == "motion":
            event_type = "motion_detected"
            threat_level = "LOW"
            context_summary = f"Ring Motion: Activity detected in {payload.location} zone."
            event_payload["zone"] = payload.location

        elif kind == "door_activity":
            event_type = "door_opened"
            event_payload["door_name"] = "Front Door"
            event_payload["state"] = "open"
            context_summary = f"Ring Sensor: Front door opened at {payload.location}."
            threat_level = "LOW"

        else:
            event_type = f"ring_{kind}"
            context_summary = f"Ring Event: {kind} received from {payload.device_name}."

        event_payload["context_summary"] = context_summary
        event_payload["threat_level"] = threat_level

        # 3. Ingest into canonical memory graph
        event_in = EventCreate(
            event_type=event_type,
            source_device=payload.device_name,
            payload=event_payload,
            occurred_at=occurred_at
        )
        ingest_res = await self.engine.ingest_event(event_in)

        # 4. Broadcast via SSE
        await broadcaster.broadcast({
            "type": "RING_EVENT",
            "event_type": event_type,
            "threat_level": threat_level,
            "context_summary": context_summary,
            "device": payload.device_name,
            "location": payload.location,
            "occurred_at": occurred_at.isoformat()
        })

        return RingEventResult(
            ring_event_id=payload.event_id,
            normalized_event_type=event_type,
            context_summary=context_summary,
            threat_level=threat_level,
            device_synced=device_entity.name,
            graph_mutations=ingest_res.graph_updates,
            persisted_event_id=str(ingest_res.event.id)
        )

    async def simulate_scenario(self, req: RingSimulationRequest) -> RingEventResult:
        """Simulates typical Ring scenarios for demo and automated test coverage."""
        now = datetime.now(timezone.utc)
        
        if req.scenario == "ding_neighbor":
            payload = RingWebhookPayload(
                kind="ding",
                person_detected=True,
                person_name=req.person_name or "Ravi",
                confidence=0.96,
                location="Front Porch",
                device_name=req.device_name or "Front Door Video Doorbell",
                occurred_at=now
            )
        elif req.scenario == "ding_stranger":
            payload = RingWebhookPayload(
                kind="ding",
                person_detected=True,
                person_name="Unknown Visitor",
                confidence=0.88,
                location="Front Porch",
                device_name=req.device_name or "Front Door Video Doorbell",
                occurred_at=now
            )
        elif req.scenario == "late_night_motion":
            late_time = now.replace(hour=2, minute=15)
            payload = RingWebhookPayload(
                kind="person_detected",
                person_detected=True,
                person_name="Unknown Person",
                confidence=0.91,
                location="Front Porch",
                device_name=req.device_name or "Front Door Video Doorbell",
                occurred_at=late_time
            )
        elif req.scenario == "motion_package":
            payload = RingWebhookPayload(
                kind="motion",
                person_detected=False,
                location="Front Porch",
                device_name=req.device_name or "Front Door Video Doorbell",
                occurred_at=now
            )
        else:
            payload = RingWebhookPayload(
                kind="motion",
                location="Front Porch",
                device_name=req.device_name or "Front Door Video Doorbell",
                occurred_at=now
            )

        return await self.process_ring_webhook(payload)
