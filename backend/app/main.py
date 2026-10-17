import os
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db, init_db
from app.seed import seed_household_graph
from app.repository.graph_repo import GraphRepository
from app.schemas.graph import (
    EntityRead, EntityCreate, RelationshipRead, RelationshipCreate,
    EntityNeighborhood
)
from app.schemas.event import EventRead, EventCreate
from app.schemas.audit import AuditLogRead
from app.mcp.router import router as mcp_router
from app.engine.router import router as ingestion_router
from app.ai.router import router as ai_router
from app.adapters.router import router as ring_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    await init_db()
    # Seed default household data for hackathon demo
    await seed_household_graph()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ContextOS - Ambient Contextual Intelligence Platform for Independent Living",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(mcp_router)
app.include_router(ingestion_router)
app.include_router(ai_router)
app.include_router(ring_router)

DASHBOARD_PATH = os.path.join(os.path.dirname(__file__), "static", "dashboard.html")

@app.get("/")
@app.get("/dashboard")
async def serve_dashboard():
    if os.path.exists(DASHBOARD_PATH):
        return FileResponse(DASHBOARD_PATH)
    return {"message": "ContextOS API running. Dashboard file not found."}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

# ---------------- GRAPH ENDPOINTS ----------------
@app.get("/api/graph/entities", response_model=List[EntityRead])
async def list_entities(
    entity_type: Optional[str] = Query(None, description="Filter by type (person, device, location, routine, object)"),
    db: AsyncSession = Depends(get_db)
):
    repo = GraphRepository(db)
    entities = await repo.list_entities(entity_type=entity_type)
    return [
        EntityRead(
            id=e.id,
            name=e.name,
            entity_type=e.entity_type,
            metadata=e.metadata_,
            created_at=e.created_at,
            updated_at=e.updated_at
        )
        for e in entities
    ]

@app.post("/api/graph/entities", response_model=EntityRead, status_code=201)
async def create_entity(
    entity_in: EntityCreate,
    db: AsyncSession = Depends(get_db)
):
    repo = GraphRepository(db)
    entity = await repo.create_entity(entity_in)
    return EntityRead(
        id=entity.id,
        name=entity.name,
        entity_type=entity.entity_type,
        metadata=entity.metadata_,
        created_at=entity.created_at,
        updated_at=entity.updated_at
    )

@app.get("/api/graph/entities/{entity_id_or_name}/neighborhood", response_model=EntityNeighborhood)
async def get_entity_neighborhood(
    entity_id_or_name: str,
    db: AsyncSession = Depends(get_db)
):
    repo = GraphRepository(db)
    neighborhood = await repo.get_entity_neighborhood(entity_id_or_name)
    if not neighborhood:
        raise HTTPException(status_code=404, detail=f"Entity '{entity_id_or_name}' not found")
    return neighborhood

@app.get("/api/graph/relationships", response_model=List[RelationshipRead])
async def list_relationships(db: AsyncSession = Depends(get_db)):
    repo = GraphRepository(db)
    relationships = await repo.list_relationships()
    return [
        RelationshipRead(
            id=r.id,
            source_entity_id=r.source_entity_id,
            target_entity_id=r.target_entity_id,
            relation_type=r.relation_type,
            weight=r.weight,
            metadata=r.metadata_,
            updated_at=r.updated_at
        )
        for r in relationships
    ]

@app.post("/api/graph/relationships", response_model=RelationshipRead, status_code=201)
async def add_relationship(
    rel_in: RelationshipCreate,
    db: AsyncSession = Depends(get_db)
):
    repo = GraphRepository(db)
    rel = await repo.add_relationship(rel_in)
    return RelationshipRead(
        id=rel.id,
        source_entity_id=rel.source_entity_id,
        target_entity_id=rel.target_entity_id,
        relation_type=rel.relation_type,
        weight=rel.weight,
        metadata=rel.metadata_,
        updated_at=rel.updated_at
    )

# ---------------- EVENTS & AUDIT ----------------
@app.get("/api/events/recent", response_model=List[EventRead])
async def get_recent_events(
    limit: int = Query(10, ge=1, le=100),
    event_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    repo = GraphRepository(db)
    events = await repo.list_recent_events(limit=limit, event_type=event_type)
    return [
        EventRead(
            id=e.id,
            event_type=e.event_type,
            source_device=e.source_device,
            payload=e.payload,
            occurred_at=e.occurred_at
        )
        for e in events
    ]

@app.get("/api/audit-logs", response_model=List[AuditLogRead])
async def list_audit_logs(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    repo = GraphRepository(db)
    logs = await repo.list_audit_logs(limit=limit)
    return [
        AuditLogRead(
            id=l.id,
            action_type=l.action_type,
            trigger_event_id=l.trigger_event_id,
            prompt_context=l.prompt_context,
            thinking_process=l.thinking_process,
            output_response=l.output_response,
            created_at=l.created_at
        )
        for l in logs
    ]
