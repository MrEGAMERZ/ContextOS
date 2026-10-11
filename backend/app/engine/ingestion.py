from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.graph_repo import GraphRepository
from app.schemas.graph import RelationshipCreate, EntityCreate
from app.schemas.event import EventCreate, EventRead, IngestEventResponse
from app.models.event import Event

class IngestionEngine:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = GraphRepository(session)

    async def ingest_event(self, event_in: EventCreate) -> IngestEventResponse:
        occurred_at = event_in.occurred_at or datetime.now(timezone.utc)
        payload = event_in.payload or {}
        event_type = event_in.event_type.lower()
        source_device = event_in.source_device

        # 1. Persist the raw normalized event
        db_event = await self.repo.create_event(
            event_type=event_type,
            source_device=source_device,
            payload=payload,
            occurred_at=occurred_at
        )

        graph_mutations: Dict[str, Any] = {}
        immediate_alerts: List[Dict[str, Any]] = []

        # 2. Handle Doorbell / Person Sighting
        if event_type in ("doorbell_rung", "person_detected", "visitor_arrived"):
            person_name = payload.get("person") or payload.get("visitor") or payload.get("name")
            location_name = payload.get("location", "Front Porch")

            if person_name:
                person = await self.repo.get_entity_by_name(person_name)
                if not person:
                    # Auto-discover or create unknown visitor entity
                    person = await self.repo.create_entity(EntityCreate(
                        name=person_name,
                        entity_type="person",
                        metadata={"auto_detected": True, "first_seen": occurred_at.isoformat()}
                    ))
                    graph_mutations["created_entity"] = person.name

                # Update person metadata
                new_meta = dict(person.metadata_ or {})
                new_meta["last_seen"] = occurred_at.isoformat()
                new_meta["last_location"] = location_name
                person.metadata_ = new_meta
                person.updated_at = occurred_at

                # Link to location
                loc_entity = await self.repo.get_entity_by_name(location_name)
                if loc_entity:
                    await self.repo.add_relationship(RelationshipCreate(
                        source_entity_id=person.id,
                        target_entity_id=loc_entity.id,
                        relation_type="visited",
                        weight=1.0,
                        metadata={"last_seen": occurred_at.isoformat(), "source": source_device}
                    ))
                    graph_mutations["relationship_updated"] = f"{person.name} -> visited -> {loc_entity.name}"

                await self.session.commit()

        # 3. Handle Object Relocation / Sighting
        elif event_type in ("object_detected", "object_moved", "object_sighting"):
            object_name = payload.get("object") or payload.get("item")
            location_name = payload.get("location")
            confidence = float(payload.get("confidence", 0.90))

            if object_name and location_name:
                obj_entity = await self.repo.get_entity_by_name(object_name)
                if not obj_entity:
                    obj_entity = await self.repo.create_entity(EntityCreate(
                        name=object_name,
                        entity_type="object",
                        metadata={"confidence": confidence}
                    ))
                    graph_mutations["created_entity"] = obj_entity.name

                new_obj_meta = dict(obj_entity.metadata_ or {})
                new_obj_meta["last_seen_location"] = location_name
                new_obj_meta["last_seen_time"] = occurred_at.isoformat()
                new_obj_meta["confidence"] = confidence
                obj_entity.metadata_ = new_obj_meta
                obj_entity.updated_at = occurred_at

                loc_entity = await self.repo.get_entity_by_name(location_name)
                if loc_entity:
                    await self.repo.add_relationship(RelationshipCreate(
                        source_entity_id=obj_entity.id,
                        target_entity_id=loc_entity.id,
                        relation_type="located_in",
                        weight=confidence,
                        metadata={"last_updated": occurred_at.isoformat(), "source": source_device}
                    ))
                    graph_mutations["relationship_updated"] = f"{obj_entity.name} -> located_in -> {loc_entity.name}"

                await self.session.commit()

        # 4. Handle Door / Window State Transitions
        elif event_type in ("door_opened", "door_closed"):
            door_name = payload.get("door", "Front Porch")
            state = "open" if event_type == "door_opened" else "closed"
            door_entity = await self.repo.get_entity_by_name(door_name)
            if door_entity:
                new_door_meta = dict(door_entity.metadata_ or {})
                new_door_meta["state"] = state
                new_door_meta["last_state_change"] = occurred_at.isoformat()
                door_entity.metadata_ = new_door_meta
                door_entity.updated_at = occurred_at
                await self.session.commit()
                graph_mutations["entity_state"] = f"{door_entity.name}: state={state}"

        # 5. Handle Routine Events
        elif event_type in ("routine_completed", "routine_performed"):
            routine_name = payload.get("routine")
            if routine_name:
                routine_entity = await self.repo.get_entity_by_name(routine_name)
                if routine_entity:
                    new_rout_meta = dict(routine_entity.metadata_ or {})
                    new_rout_meta["last_completed"] = occurred_at.isoformat()
                    routine_entity.metadata_ = new_rout_meta
                    routine_entity.updated_at = occurred_at
                    await self.session.commit()
                    graph_mutations["routine_updated"] = f"{routine_entity.name}: completed"

        return IngestEventResponse(
            status="success",
            event=EventRead(
                id=db_event.id,
                event_type=db_event.event_type,
                source_device=db_event.source_device,
                payload=db_event.payload,
                occurred_at=db_event.occurred_at
            ),
            graph_updates=graph_mutations,
            immediate_alerts=immediate_alerts
        )
