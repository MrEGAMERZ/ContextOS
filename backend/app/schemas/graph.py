from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Dict, Any, List, Optional

class EntityBase(BaseModel):
    name: str = Field(..., description="Unique or canonical name of the entity")
    entity_type: str = Field(..., description="Entity classification: person, device, location, routine, object")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary attributes, e.g. role, relationship")

class EntityCreate(EntityBase):
    id: Optional[str] = None

class EntityRead(EntityBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RelationshipBase(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relation_type: str
    weight: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

class RelationshipCreate(RelationshipBase):
    pass

class RelationshipRead(RelationshipBase):
    id: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NeighborNode(BaseModel):
    entity: EntityRead
    relation_type: str
    direction: str # outgoing or incoming
    weight: float
    metadata: Dict[str, Any]

class EntityNeighborhood(BaseModel):
    center: EntityRead
    immediate_neighbors: List[NeighborNode]
    two_hop_neighbors: List[NeighborNode]
    recent_events: List[Dict[str, Any]] = Field(default_factory=list)
