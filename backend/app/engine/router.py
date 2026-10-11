from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.event import EventCreate, IngestEventResponse
from app.engine.ingestion import IngestionEngine

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.post("/ingest", response_model=IngestEventResponse, status_code=201)
async def ingest_event(
    event_in: EventCreate,
    db: AsyncSession = Depends(get_db)
):
    engine = IngestionEngine(db)
    return await engine.ingest_event(event_in)
