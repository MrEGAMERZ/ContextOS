"""FastAPI router for Ring device perception and webhooks."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.entity import Entity
from app.models.event import Event
from app.adapters.ring_adapter import (
    RingAdapter,
    RingWebhookPayload,
    RingSimulationRequest,
    RingEventResult
)

router = APIRouter(prefix="/api/ring", tags=["Ring Perception Adapter"])


@router.post("/webhook", response_model=RingEventResult)
async def handle_ring_webhook(
    payload: RingWebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    """Receive live webhook from Ring Cloud API / Simulator and ingest into ContextOS."""
    adapter = RingAdapter(db)
    return await adapter.process_ring_webhook(payload)


@router.post("/simulate", response_model=RingEventResult)
async def simulate_ring_event(
    req: RingSimulationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Trigger a simulated Ring event for hackathon testing and live judge demonstrations."""
    adapter = RingAdapter(db)
    return await adapter.simulate_scenario(req)


@router.get("/devices")
async def list_ring_devices(db: AsyncSession = Depends(get_db)):
    """List all Ring devices synced into the Memory Graph."""
    res = await db.execute(select(Entity).where(Entity.entity_type == "device"))
    devices = res.scalars().all()
    ring_devices = []
    for d in devices:
        meta = d.metadata_ or {}
        if meta.get("hardware_type") == "ring_doorbell" or "ring" in d.name.lower():
            ring_devices.append({
                "id": str(d.id),
                "name": d.name,
                "location": meta.get("location", "Front Porch"),
                "battery_level": meta.get("battery_level", 100),
                "last_ping": meta.get("last_ping")
            })
    return {"ring_devices": ring_devices, "count": len(ring_devices)}


@router.get("/recent")
async def list_recent_ring_events(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """Retrieve recent Ring perception events from the persistent audit stream."""
    res = await db.execute(
        select(Event)
        .order_by(Event.occurred_at.desc())
        .limit(limit * 2)
    )
    events = res.scalars().all()
    ring_events = []
    for e in events:
        payload = e.payload or {}
        if payload.get("source_hardware") == "Ring" or "ring" in e.source_device.lower():
            ring_events.append({
                "id": str(e.id),
                "event_type": e.event_type,
                "source_device": e.source_device,
                "occurred_at": e.occurred_at.isoformat() if e.occurred_at else None,
                "context_summary": payload.get("context_summary"),
                "threat_level": payload.get("threat_level", "LOW"),
                "snapshot_url": payload.get("snapshot_url")
            })
            if len(ring_events) >= limit:
                break
    return {"events": ring_events}
