from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.graph_repo import GraphRepository
from app.ai.agent import ContextOSAgent
from app.engine.stream import broadcaster

class AnomalyDetector:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = GraphRepository(session)
        self.agent = ContextOSAgent(session)

    async def evaluate_tick(self, current_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        now = current_time or datetime.now(timezone.utc)
        detected_anomalies: List[Dict[str, Any]] = []

        all_entities = await self.repo.list_entities()

        # Rule 1: Check Door Open Duration (>30 minutes)
        for entity in all_entities:
            meta = entity.metadata_ or {}
            if meta.get("state") == "open":
                last_change_str = meta.get("last_state_change")
                if last_change_str:
                    try:
                        last_change = datetime.fromisoformat(last_change_str)
                        if (now - last_change) > timedelta(minutes=30):
                            duration_min = round((now - last_change).total_seconds() / 60)
                            anomaly_desc = f"Door '{entity.name}' has been left OPEN for {duration_min} minutes."
                            
                            # Log anomaly event
                            evt = await self.repo.create_event(
                                event_type="omission_detected",
                                source_device="contextos_temporal_clock",
                                payload={
                                    "target": entity.name,
                                    "rule": "door_open_exceeded_threshold",
                                    "duration_minutes": duration_min,
                                    "severity": "high"
                                },
                                occurred_at=now
                            )

                            # Invoke deep reasoning Bedrock pipeline
                            ai_result = await self.agent.deep_reasoning_inference(
                                event_id=evt.id,
                                topic=anomaly_desc,
                                context_subgraph={
                                    "entity": entity.name,
                                    "state": "open",
                                    "duration_minutes": duration_min,
                                    "threshold_minutes": 30
                                }
                            )

                            anomaly_record = {
                                "type": "door_open_omission",
                                "title": "Safety Risk: Door Left Open",
                                "description": anomaly_desc,
                                "event_id": evt.id,
                                "audit_id": ai_result["audit_id"],
                                "thinking_process": ai_result["thinking_process"],
                                "recommendation": ai_result["analysis"],
                                "occurred_at": now.isoformat()
                            }
                            detected_anomalies.append(anomaly_record)
                            await broadcaster.broadcast({
                                "type": "anomaly_alert",
                                "data": anomaly_record
                            })
                    except Exception:
                        pass

        # Rule 2: Check Missed Medication Routine
        for entity in all_entities:
            if entity.entity_type == "routine":
                meta = entity.metadata_ or {}
                if "Medication" in entity.name:
                    last_completed_str = meta.get("last_completed")
                    missed = False
                    if not last_completed_str:
                        missed = True
                    else:
                        try:
                            last_comp = datetime.fromisoformat(last_completed_str)
                            if (now - last_comp) > timedelta(hours=14):
                                missed = True
                        except Exception:
                            missed = True

                    if missed:
                        anomaly_desc = f"Routine '{entity.name}' was not completed during scheduled morning window."
                        evt = await self.repo.create_event(
                            event_type="routine_missed",
                            source_device="contextos_temporal_clock",
                            payload={
                                "target": entity.name,
                                "rule": "routine_omission",
                                "window_end": meta.get("window_end", "09:30"),
                                "severity": "medium"
                            },
                            occurred_at=now
                        )

                        ai_result = await self.agent.deep_reasoning_inference(
                            event_id=evt.id,
                            topic=anomaly_desc,
                            context_subgraph={
                                "routine": entity.name,
                                "last_completed": last_completed_str,
                                "expected_window": "08:00 - 09:30"
                            }
                        )

                        anomaly_record = {
                            "type": "routine_missed_omission",
                            "title": "Health Routine Omission",
                            "description": anomaly_desc,
                            "event_id": evt.id,
                            "audit_id": ai_result["audit_id"],
                            "thinking_process": ai_result["thinking_process"],
                            "recommendation": ai_result["analysis"],
                            "occurred_at": now.isoformat()
                        }
                        detected_anomalies.append(anomaly_record)
                        await broadcaster.broadcast({
                            "type": "anomaly_alert",
                            "data": anomaly_record
                        })

        # Rule 3: Check Wandering / Late Night Exterior Door Open (23:00 - 05:00)
        hour = now.hour
        is_night = (hour >= 23 or hour < 5)
        if is_night:
            for entity in all_entities:
                meta = entity.metadata_ or {}
                if meta.get("state") == "open" and ("door" in entity.name.lower() or "entrance" in entity.name.lower()):
                    anomaly_desc = f"Wandering Risk: Exterior door '{entity.name}' opened during late night ({now.strftime('%H:%M')})."
                    evt = await self.repo.create_event(
                        event_type="wandering_risk_detected",
                        source_device="contextos_temporal_clock",
                        payload={
                            "target": entity.name,
                            "rule": "nighttime_wandering_risk",
                            "time": now.strftime("%H:%M"),
                            "severity": "high"
                        },
                        occurred_at=now
                    )

                    ai_result = await self.agent.deep_reasoning_inference(
                        event_id=evt.id,
                        topic=anomaly_desc,
                        context_subgraph={
                            "entity": entity.name,
                            "state": "open",
                            "hour": hour,
                            "risk": "dementia_wandering_risk"
                        }
                    )

                    anomaly_record = {
                        "type": "wandering_alert",
                        "title": "Critical: Nighttime Wandering Risk",
                        "description": anomaly_desc,
                        "event_id": evt.id,
                        "audit_id": ai_result["audit_id"],
                        "thinking_process": ai_result["thinking_process"],
                        "recommendation": ai_result["analysis"],
                        "occurred_at": now.isoformat()
                    }
                    detected_anomalies.append(anomaly_record)
                    await broadcaster.broadcast({
                        "type": "anomaly_alert",
                        "data": anomaly_record
                    })

        # Rule 4: Check Extended Bathroom Inactivity (Potential Fall / Distress)
        for entity in all_entities:
            meta = entity.metadata_ or {}
            if "bathroom" in entity.name.lower():
                if meta.get("occupied") is True:
                    entry_time_str = meta.get("occupied_since")
                    if entry_time_str:
                        try:
                            entry_time = datetime.fromisoformat(entry_time_str)
                            if (now - entry_time) > timedelta(minutes=45):
                                duration_min = round((now - entry_time).total_seconds() / 60)
                                anomaly_desc = f"Fall Risk Alert: Bathroom occupied for {duration_min} minutes with no motion detected."
                                evt = await self.repo.create_event(
                                    event_type="fall_risk_detected",
                                    source_device="contextos_temporal_clock",
                                    payload={
                                        "target": entity.name,
                                        "rule": "bathroom_extended_inactivity",
                                        "duration_minutes": duration_min,
                                        "severity": "high"
                                    },
                                    occurred_at=now
                                )

                                ai_result = await self.agent.deep_reasoning_inference(
                                    event_id=evt.id,
                                    topic=anomaly_desc,
                                    context_subgraph={
                                        "location": entity.name,
                                        "duration_minutes": duration_min,
                                        "risk": "possible_fall_or_distress"
                                    }
                                )

                                anomaly_record = {
                                    "type": "fall_risk_alert",
                                    "title": "Urgent: Potential Bathroom Fall Detected",
                                    "description": anomaly_desc,
                                    "event_id": evt.id,
                                    "audit_id": ai_result["audit_id"],
                                    "thinking_process": ai_result["thinking_process"],
                                    "recommendation": ai_result["analysis"],
                                    "occurred_at": now.isoformat()
                                }
                                detected_anomalies.append(anomaly_record)
                                await broadcaster.broadcast({
                                    "type": "anomaly_alert",
                                    "data": anomaly_record
                                })
                        except Exception:
                            pass

        return detected_anomalies

