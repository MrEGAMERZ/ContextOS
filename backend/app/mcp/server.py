import time
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.graph_repo import GraphRepository

# Formal MCP Tool Schemas exposed to Alexa+ / Bedrock Agents
MCP_TOOLS_SPEC = [
    {
        "name": "get_entity_context",
        "description": "Retrieves the 2-hop relational neighborhood and recent observations for an entity in the home (e.g. a person, object, device, room, or routine).",
        "parameters": {
            "type": "object",
            "properties": {
                "entity_name": {
                    "type": "string",
                    "description": "Name or identifier of the entity, e.g. 'Ravi', 'Reading Glasses', 'Arthur', 'Front Porch'."
                }
            },
            "required": ["entity_name"]
        }
    },
    {
        "name": "get_recent_events",
        "description": "Returns a chronological stream of recent smart home sensory events, door open/close transitions, or visitor arrivals.",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "description": "Maximum number of events to return."
                },
                "event_type": {
                    "type": "string",
                    "description": "Optional filter for event type, e.g. 'doorbell_rung', 'door_opened', 'person_detected'."
                }
            }
        }
    },
    {
        "name": "query_memory_graph",
        "description": "Performs a fast semantic lookup across entities, relationships, and active temporal constraints in the home memory graph.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search term or entity query, e.g. 'glasses', 'neighbor', 'visitor', 'medicine'."
                }
            },
            "required": ["query"]
        }
    }
]

class MCPServer:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = GraphRepository(session)

    async def list_tools(self) -> List[Dict[str, Any]]:
        return MCP_TOOLS_SPEC

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.perf_counter()

        if tool_name == "get_entity_context":
            result = await self._tool_get_entity_context(arguments.get("entity_name", ""))
        elif tool_name == "get_recent_events":
            result = await self._tool_get_recent_events(
                limit=int(arguments.get("limit", 10)),
                event_type=arguments.get("event_type")
            )
        elif tool_name == "query_memory_graph":
            result = await self._tool_query_memory_graph(arguments.get("query", ""))
        else:
            return {
                "error": f"Unknown tool: '{tool_name}'",
                "execution_ms": round((time.perf_counter() - start_time) * 1000, 2)
            }

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "tool": tool_name,
            "data": result,
            "execution_ms": elapsed_ms,
            "sla_pass": elapsed_ms < 50.0 # Voice turn SLA guarantee
        }

    async def _tool_get_entity_context(self, entity_name: str) -> Dict[str, Any]:
        neighborhood = await self.repo.get_entity_neighborhood(entity_name)
        if not neighborhood:
            return {"found": False, "message": f"Entity '{entity_name}' not found in ContextOS Memory Graph."}

        immediate_relations = [
            {
                "target": n.entity.name,
                "type": n.entity.entity_type,
                "relation": n.relation_type,
                "direction": n.direction,
                "weight": n.weight,
                "metadata": n.metadata
            }
            for n in neighborhood.immediate_neighbors
        ]

        two_hop_relations = [
            {
                "target": n.entity.name,
                "type": n.entity.entity_type,
                "relation": n.relation_type,
                "direction": n.direction
            }
            for n in neighborhood.two_hop_neighbors
        ]

        return {
            "found": True,
            "entity": {
                "id": neighborhood.center.id,
                "name": neighborhood.center.name,
                "entity_type": neighborhood.center.entity_type,
                "metadata": neighborhood.center.metadata
            },
            "immediate_context": immediate_relations,
            "extended_context": two_hop_relations,
            "recent_observations": neighborhood.recent_events
        }

    async def _tool_get_recent_events(self, limit: int = 10, event_type: Optional[str] = None) -> Dict[str, Any]:
        events = await self.repo.list_recent_events(limit=limit, event_type=event_type)
        return {
            "count": len(events),
            "events": [
                {
                    "id": e.id,
                    "event_type": e.event_type,
                    "source_device": e.source_device,
                    "payload": e.payload,
                    "occurred_at": e.occurred_at.isoformat()
                }
                for e in events
            ]
        }

    async def _tool_query_memory_graph(self, query: str) -> Dict[str, Any]:
        query_lower = query.strip().lower()
        all_entities = await self.repo.list_entities()
        matched_entities = []

        for e in all_entities:
            score = 0
            if query_lower in e.name.lower():
                score += 3
            if query_lower in e.entity_type.lower():
                score += 2
            meta_str = json.dumps(e.metadata_).lower()
            if query_lower in meta_str:
                score += 1

            if score > 0:
                matched_entities.append({
                    "id": e.id,
                    "name": e.name,
                    "entity_type": e.entity_type,
                    "relevance_score": score,
                    "metadata": e.metadata_
                })

        # Sort by relevance
        matched_entities.sort(key=lambda x: x["relevance_score"], reverse=True)
        return {
            "query": query,
            "results_count": len(matched_entities),
            "matches": matched_entities[:10]
        }
