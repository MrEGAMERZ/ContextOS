from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.engine.ingestion import IngestionEngine
from app.engine.anomaly import AnomalyDetector
from app.engine.stream import broadcaster
from app.schemas.event import EventCreate
from app.schemas.graph import EntityCreate
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

        elif scenario_name in ("wandering_nighttime", "nighttime_wandering"):
            # Scenario 5: Wandering Risk (Door opened at 2:30 AM)
            door = await self.repo.get_entity_by_name("Front Door")
            if not door:
                door = await self.repo.create_entity(EntityCreate(name="Front Door", entity_type="device", metadata={"state": "closed"}))
            
            night_time = now.replace(hour=2, minute=30)
            meta = dict(door.metadata_ or {})
            meta["state"] = "open"
            meta["last_state_change"] = night_time.isoformat()
            door.metadata_ = meta
            door.updated_at = night_time
            await self.session.commit()

            anomalies = await self.anomaly.evaluate_tick(current_time=night_time)
            return {
                "scenario": scenario_name,
                "description": "Simulated late night wandering risk (Front door open at 02:30 AM).",
                "anomalies_detected": anomalies
            }

        elif scenario_name in ("bathroom_fall", "bathroom_inactivity"):
            # Scenario 6: Potential Fall in Bathroom
            bathroom = await self.repo.get_entity_by_name("Master Bathroom")
            if not bathroom:
                bathroom = await self.repo.create_entity(EntityCreate(name="Master Bathroom", entity_type="location"))
            
            fifty_mins_ago = (now - timedelta(minutes=50)).isoformat()
            meta = dict(bathroom.metadata_ or {})
            meta["occupied"] = True
            meta["occupied_since"] = fifty_mins_ago
            bathroom.metadata_ = meta
            bathroom.updated_at = now
            await self.session.commit()

            anomalies = await self.anomaly.evaluate_tick(current_time=now)
            return {
                "scenario": scenario_name,
                "description": "Simulated extended bathroom inactivity (Potential fall after 50 minutes).",
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
