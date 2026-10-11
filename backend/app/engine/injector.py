from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.engine.ingestion import IngestionEngine
from app.engine.anomaly import AnomalyDetector
from app.engine.stream import broadcaster
from app.schemas.event import EventCreate
from app.repository.graph_repo import GraphRepository

class EventInjector:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.ingestion = IngestionEngine(session)
        self.anomaly = AnomalyDetector(session)
        self.repo = GraphRepository(session)

    async def inject_scenario(self, scenario_name: str, custom_payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)

        if scenario_name == "visitor_arrival":
            # Scenario 1: Ring Doorbell detects Ravi at Front Porch
            event = EventCreate(
                event_type="doorbell_rung",
                source_device="ring_front_door",
                payload={
                    "visitor": "Ravi",
                    "location": "Front Porch",
                    "relationship": "Neighbor",
                    "confidence": 0.98,
                    "expected_reason": "Discuss garden tomato seedlings"
                },
                occurred_at=now
            )
            ingest_res = await self.ingestion.ingest_event(event)
            await broadcaster.broadcast({
                "type": "scenario_triggered",
                "scenario": scenario_name,
                "event": ingest_res.event.model_dump(mode="json"),
                "graph_updates": ingest_res.graph_updates
            })
            return {
                "scenario": scenario_name,
                "description": "Triggered visitor arrival for neighbor Ravi at front door.",
                "ingest_result": ingest_res.model_dump(mode="json")
            }

        elif scenario_name == "object_relocation":
            # Scenario 2: Reading Glasses moved to Kitchen Counter
            event = EventCreate(
                event_type="object_moved",
                source_device="kitchen_camera",
                payload={
                    "object": "Reading Glasses",
                    "location": "Kitchen",
                    "confidence": 0.96
                },
                occurred_at=now
            )
            ingest_res = await self.ingestion.ingest_event(event)
            await broadcaster.broadcast({
                "type": "scenario_triggered",
                "scenario": scenario_name,
                "event": ingest_res.event.model_dump(mode="json"),
                "graph_updates": ingest_res.graph_updates
            })
            return {
                "scenario": scenario_name,
                "description": "Moved reading glasses to kitchen.",
                "ingest_result": ingest_res.model_dump(mode="json")
            }

        elif scenario_name == "front_door_open_anomaly":
            # Scenario 3: Door left open for 35 minutes
            door = await self.repo.get_entity_by_name("Front Porch")
            if door:
                door_meta = dict(door.metadata_ or {})
                door_meta["state"] = "open"
                door_meta["last_state_change"] = (now - timedelta(minutes=35)).isoformat()
                door.metadata_ = door_meta
                await self.session.commit()

            anomalies = await self.anomaly.evaluate_tick(current_time=now)
            return {
                "scenario": scenario_name,
                "description": "Simulated front door left open for 35 minutes.",
                "anomalies_detected": anomalies
            }

        elif scenario_name == "missed_medication":
            # Scenario 4: Morning medication omitted
            routine = await self.repo.get_entity_by_name("Morning Medication Routine")
            if routine:
                rout_meta = dict(routine.metadata_ or {})
                rout_meta["last_completed"] = (now - timedelta(hours=26)).isoformat()
                routine.metadata_ = rout_meta
                await self.session.commit()

            anomalies = await self.anomaly.evaluate_tick(current_time=now)
            return {
                "scenario": scenario_name,
                "description": "Simulated missed morning medication routine.",
                "anomalies_detected": anomalies
            }

        else:
            # Custom event
            payload = custom_payload or {}
            event = EventCreate(
                event_type=payload.get("event_type", "custom_event"),
                source_device=payload.get("source_device", "simulator"),
                payload=payload.get("payload", {}),
                occurred_at=now
            )
            ingest_res = await self.ingestion.ingest_event(event)
            await broadcaster.broadcast({
                "type": "scenario_triggered",
                "scenario": "custom",
                "event": ingest_res.event.model_dump(mode="json"),
                "graph_updates": ingest_res.graph_updates
            })
            return {
                "scenario": "custom",
                "ingest_result": ingest_res.model_dump(mode="json")
            }
