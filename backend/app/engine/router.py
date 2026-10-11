from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.event import EventCreate, IngestEventResponse
from app.engine.ingestion import IngestionEngine
from app.engine.anomaly import AnomalyDetector
from app.engine.injector import EventInjector
from app.engine.stream import broadcaster
from app.repository.graph_repo import GraphRepository

router = APIRouter(tags=["Engine & Events"])

class InjectRequest(BaseModel):
    scenario: str = Field(..., description="Scenario name: visitor_arrival, object_relocation, front_door_open_anomaly, missed_medication, or custom")
    payload: Optional[Dict[str, Any]] = None

@router.post("/api/events/ingest", response_model=IngestEventResponse, status_code=201)
async def ingest_event(
    event_in: EventCreate,
    db: AsyncSession = Depends(get_db)
):
    engine = IngestionEngine(db)
    res = await engine.ingest_event(event_in)
    await broadcaster.broadcast({
        "type": "event_ingested",
        "event": res.event.model_dump(mode="json"),
        "graph_updates": res.graph_updates
    })
    return res

@router.post("/api/events/inject")
async def inject_scenario(
    req: InjectRequest,
    db: AsyncSession = Depends(get_db)
):
    injector = EventInjector(db)
    return await injector.inject_scenario(req.scenario, req.payload)

@router.post("/api/engine/tick")
async def evaluate_temporal_tick(db: AsyncSession = Depends(get_db)):
    detector = AnomalyDetector(db)
    anomalies = await detector.evaluate_tick()
    return {
        "status": "success",
        "tick_executed_at": "now",
        "anomalies_detected_count": len(anomalies),
        "anomalies": anomalies
    }

@router.get("/api/events/stream")
async def stream_live_events(request: Request):
    """Server-Sent Events (SSE) live feed for Caregiver Dashboard and Graph animations"""
    return StreamingResponse(
        broadcaster.stream_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
