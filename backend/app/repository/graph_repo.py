from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, desc
from sqlalchemy.orm import selectinload
from app.models.entity import Entity
from app.models.relationship import Relationship
from app.models.event import Event
from app.models.audit import ActionAuditLog
from app.schemas.graph import EntityCreate, RelationshipCreate, EntityRead, NeighborNode, EntityNeighborhood

class GraphRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # ------------------ ENTITIES ------------------
    async def create_entity(self, entity_in: EntityCreate) -> Entity:
        entity = Entity(
            id=entity_in.id,
            name=entity_in.name,
            entity_type=entity_in.entity_type,
            metadata_=entity_in.metadata
        )
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def get_entity_by_id(self, entity_id: str) -> Optional[Entity]:
        stmt = (
            select(Entity)
            .where(Entity.id == entity_id)
            .options(
                selectinload(Entity.outgoing_relationships).selectinload(Relationship.target_entity),
                selectinload(Entity.incoming_relationships).selectinload(Relationship.source_entity),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_entity_by_name(self, name: str) -> Optional[Entity]:
        stmt = (
            select(Entity)
            .where(Entity.name.ilike(name))
            .options(
                selectinload(Entity.outgoing_relationships).selectinload(Relationship.target_entity),
                selectinload(Entity.incoming_relationships).selectinload(Relationship.source_entity),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_entities(self, entity_type: Optional[str] = None) -> List[Entity]:
        stmt = select(Entity)
        if entity_type:
            stmt = stmt.where(Entity.entity_type == entity_type)
        stmt = stmt.order_by(Entity.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ------------------ RELATIONSHIPS ------------------
    async def add_relationship(self, rel_in: RelationshipCreate) -> Relationship:
        stmt = select(Relationship).where(
            and_(
                Relationship.source_entity_id == rel_in.source_entity_id,
                Relationship.target_entity_id == rel_in.target_entity_id,
                Relationship.relation_type == rel_in.relation_type,
            )
        )
        existing = (await self.session.execute(stmt)).scalar_one_or_none()
        if existing:
            existing.weight = rel_in.weight
            existing.metadata_ = rel_in.metadata
            existing.updated_at = datetime.now(timezone.utc)
            await self.session.commit()
            await self.session.refresh(existing)
            return existing

        rel = Relationship(
            source_entity_id=rel_in.source_entity_id,
            target_entity_id=rel_in.target_entity_id,
            relation_type=rel_in.relation_type,
            weight=rel_in.weight,
            metadata_=rel_in.metadata
        )
        self.session.add(rel)
        await self.session.commit()
        await self.session.refresh(rel)
        return rel

    async def list_relationships(self) -> List[Relationship]:
        stmt = (
            select(Relationship)
            .options(
                selectinload(Relationship.source_entity),
                selectinload(Relationship.target_entity)
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # ------------------ 2-HOP NEIGHBORHOOD ------------------
    async def get_entity_neighborhood(self, entity_id_or_name: str) -> Optional[EntityNeighborhood]:
        center = await self.get_entity_by_name(entity_id_or_name)
        if not center:
            center = await self.get_entity_by_id(entity_id_or_name)
        if not center:
            return None

        immediate_nodes: List[NeighborNode] = []
        hop_1_entity_ids = set()

        # Query outgoing relationships
        stmt_out = (
            select(Relationship)
            .where(Relationship.source_entity_id == center.id)
            .options(selectinload(Relationship.target_entity))
        )
        out_rels = (await self.session.execute(stmt_out)).scalars().all()
        for out_rel in out_rels:
            target = out_rel.target_entity
            immediate_nodes.append(NeighborNode(
                entity=EntityRead(
                    id=target.id,
                    name=target.name,
                    entity_type=target.entity_type,
                    metadata=target.metadata_,
                    created_at=target.created_at,
                    updated_at=target.updated_at
                ),
                relation_type=out_rel.relation_type,
                direction="outgoing",
                weight=out_rel.weight,
                metadata=out_rel.metadata_
            ))
            hop_1_entity_ids.add(target.id)

        # Query incoming relationships
        stmt_in = (
            select(Relationship)
            .where(Relationship.target_entity_id == center.id)
            .options(selectinload(Relationship.source_entity))
        )
        in_rels = (await self.session.execute(stmt_in)).scalars().all()
        for in_rel in in_rels:
            source = in_rel.source_entity
            immediate_nodes.append(NeighborNode(
                entity=EntityRead(
                    id=source.id,
                    name=source.name,
                    entity_type=source.entity_type,
                    metadata=source.metadata_,
                    created_at=source.created_at,
                    updated_at=source.updated_at
                ),
                relation_type=in_rel.relation_type,
                direction="incoming",
                weight=in_rel.weight,
                metadata=in_rel.metadata_
            ))
            hop_1_entity_ids.add(source.id)

        two_hop_nodes: List[NeighborNode] = []
        for h1_id in hop_1_entity_ids:
            stmt_h1_out = (
                select(Relationship)
                .where(Relationship.source_entity_id == h1_id)
                .options(selectinload(Relationship.target_entity))
            )
            for out_rel in (await self.session.execute(stmt_h1_out)).scalars().all():
                if out_rel.target_entity_id != center.id and out_rel.target_entity_id not in hop_1_entity_ids:
                    target = out_rel.target_entity
                    two_hop_nodes.append(NeighborNode(
                        entity=EntityRead(
                            id=target.id,
                            name=target.name,
                            entity_type=target.entity_type,
                            metadata=target.metadata_,
                            created_at=target.created_at,
                            updated_at=target.updated_at
                        ),
                        relation_type=out_rel.relation_type,
                        direction="outgoing",
                        weight=out_rel.weight,
                        metadata=out_rel.metadata_
                    ))

            stmt_h1_in = (
                select(Relationship)
                .where(Relationship.target_entity_id == h1_id)
                .options(selectinload(Relationship.source_entity))
            )
            for in_rel in (await self.session.execute(stmt_h1_in)).scalars().all():
                if in_rel.source_entity_id != center.id and in_rel.source_entity_id not in hop_1_entity_ids:
                    source = in_rel.source_entity
                    two_hop_nodes.append(NeighborNode(
                        entity=EntityRead(
                            id=source.id,
                            name=source.name,
                            entity_type=source.entity_type,
                            metadata=source.metadata_,
                            created_at=source.created_at,
                            updated_at=source.updated_at
                        ),
                        relation_type=in_rel.relation_type,
                        direction="incoming",
                        weight=in_rel.weight,
                        metadata=in_rel.metadata_
                    ))

        recent_events = await self.get_recent_events_for_entity(center.name, limit=5)

        return EntityNeighborhood(
            center=EntityRead(
                id=center.id,
                name=center.name,
                entity_type=center.entity_type,
                metadata=center.metadata_,
                created_at=center.created_at,
                updated_at=center.updated_at
            ),
            immediate_neighbors=immediate_nodes,
            two_hop_neighbors=two_hop_nodes,
            recent_events=[
                {
                    "id": evt.id,
                    "event_type": evt.event_type,
                    "source_device": evt.source_device,
                    "payload": evt.payload,
                    "occurred_at": evt.occurred_at.isoformat()
                }
                for evt in recent_events
            ]
        )

    # ------------------ EVENTS ------------------
    async def create_event(self, event_type: str, source_device: str, payload: Dict[str, Any], occurred_at: Optional[datetime] = None) -> Event:
        evt = Event(
            event_type=event_type,
            source_device=source_device,
            payload=payload,
            occurred_at=occurred_at or datetime.now(timezone.utc)
        )
        self.session.add(evt)
        await self.session.commit()
        await self.session.refresh(evt)
        return evt

    async def list_recent_events(self, limit: int = 10, event_type: Optional[str] = None) -> List[Event]:
        stmt = select(Event)
        if event_type:
            stmt = stmt.where(Event.event_type == event_type)
        stmt = stmt.order_by(desc(Event.occurred_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recent_events_for_entity(self, entity_name: str, limit: int = 5) -> List[Event]:
        stmt = select(Event).order_by(desc(Event.occurred_at)).limit(50)
        result = await self.session.execute(stmt)
        all_events = list(result.scalars().all())
        name_lower = entity_name.lower()
        matched = []
        for evt in all_events:
            p_str = str(evt.payload).lower()
            if name_lower in p_str:
                matched.append(evt)
                if len(matched) >= limit:
                    break
        return matched

    # ------------------ AUDIT LOGS ------------------
    async def log_action(self, action_type: str, prompt_context: str, thinking_process: str, output_response: str, trigger_event_id: Optional[str] = None) -> ActionAuditLog:
        audit = ActionAuditLog(
            action_type=action_type,
            trigger_event_id=trigger_event_id,
            prompt_context=prompt_context,
            thinking_process=thinking_process,
            output_response=output_response,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(audit)
        await self.session.commit()
        await self.session.refresh(audit)
        return audit

    async def list_audit_logs(self, limit: int = 20) -> List[ActionAuditLog]:
        stmt = select(ActionAuditLog).order_by(desc(ActionAuditLog.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
