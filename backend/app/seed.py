import asyncio
from datetime import datetime, timezone, timedelta
from app.database import AsyncSessionLocal, init_db
from app.repository.graph_repo import GraphRepository
from app.schemas.graph import EntityCreate, RelationshipCreate

async def seed_household_graph():
    await init_db()
    async with AsyncSessionLocal() as session:
        repo = GraphRepository(session)
        
        # Check if already seeded
        existing = await repo.get_entity_by_name("Arthur")
        if existing:
            print("Database already contains seed entities. Skipping seed.")
            return

        print("Seeding ContextOS Household Memory Graph...")

        # 1. People
        arthur = await repo.create_entity(EntityCreate(
            name="Arthur",
            entity_type="person",
            metadata={"role": "homeowner", "age": 78, "condition": "mild_cognitive_fatigue", "lives_alone": True}
        ))

        ravi = await repo.create_entity(EntityCreate(
            name="Ravi",
            entity_type="person",
            metadata={
                "role": "neighbor",
                "phone": "+1-555-0192",
                "notes": "Spoke yesterday about garden tomato plants; expected today around 4:00 PM."
            }
        ))

        sarah = await repo.create_entity(EntityCreate(
            name="Sarah",
            entity_type="person",
            metadata={
                "role": "daughter",
                "phone": "+1-555-0144",
                "caregiver_tier": "primary",
                "notes": "Visits weekly; receives proactive caregiver summaries."
            }
        ))

        # 2. Locations
        front_door = await repo.create_entity(EntityCreate(
            name="Front Porch",
            entity_type="location",
            metadata={"type": "entrance", "camera_covered": True}
        ))

        living_room = await repo.create_entity(EntityCreate(
            name="Living Room",
            entity_type="location",
            metadata={"type": "main_living_area", "primary_occupancy": True}
        ))

        kitchen = await repo.create_entity(EntityCreate(
            name="Kitchen",
            entity_type="location",
            metadata={"type": "utility", "has_appliances": True}
        ))

        # 3. Objects
        glasses = await repo.create_entity(EntityCreate(
            name="Reading Glasses",
            entity_type="object",
            metadata={
                "description": "Black wireframe reading glasses",
                "last_seen_location": "Living Room Table",
                "last_seen_time": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
                "confidence": 0.94
            }
        ))

        med_kit = await repo.create_entity(EntityCreate(
            name="Daily Medication Box",
            entity_type="object",
            metadata={
                "schedule": "08:30 AM",
                "location": "Kitchen Counter",
                "importance": "critical"
            }
        ))

        # 4. Devices
        ring_cam = await repo.create_entity(EntityCreate(
            name="Ring Video Doorbell Pro",
            entity_type="device",
            metadata={"vendor": "Ring", "model": "Video Doorbell Pro 2", "location": "Front Porch"}
        ))

        alexa_echo = await repo.create_entity(EntityCreate(
            name="Alexa Echo Show 8",
            entity_type="device",
            metadata={"vendor": "Amazon", "capabilities": ["voice", "mcp_client", "screen"], "location": "Living Room"}
        ))

        # 5. Routines
        morning_med_routine = await repo.create_entity(EntityCreate(
            name="Morning Medication Routine",
            entity_type="routine",
            metadata={
                "window_start": "08:00",
                "window_end": "09:30",
                "criticality": "high",
                "target_object": "Daily Medication Box"
            }
        ))

        # 6. Relationships
        # Ravi neighbor to Arthur
        await repo.add_relationship(RelationshipCreate(
            source_entity_id=ravi.id,
            target_entity_id=arthur.id,
            relation_type="neighbor_of",
            weight=1.0,
            metadata={"visit_frequency": "regular", "trusted": True}
        ))

        # Sarah daughter of Arthur
        await repo.add_relationship(RelationshipCreate(
            source_entity_id=sarah.id,
            target_entity_id=arthur.id,
            relation_type="daughter_of",
            weight=1.0,
            metadata={"is_emergency_contact": True}
        ))

        # Devices located in locations
        await repo.add_relationship(RelationshipCreate(
            source_entity_id=ring_cam.id,
            target_entity_id=front_door.id,
            relation_type="located_in",
            weight=1.0,
            metadata={}
        ))

        await repo.add_relationship(RelationshipCreate(
            source_entity_id=alexa_echo.id,
            target_entity_id=living_room.id,
            relation_type="located_in",
            weight=1.0,
            metadata={}
        ))

        # Glasses located in Living Room
        await repo.add_relationship(RelationshipCreate(
            source_entity_id=glasses.id,
            target_entity_id=living_room.id,
            relation_type="located_in",
            weight=0.94,
            metadata={"sub_location": "Coffee Table"}
        ))

        # Arthur participates in Morning Med Routine
        await repo.add_relationship(RelationshipCreate(
            source_entity_id=arthur.id,
            target_entity_id=morning_med_routine.id,
            relation_type="participates_in",
            weight=1.0,
            metadata={}
        ))

        # 7. Initial Historical Events
        await repo.create_event(
            event_type="conversation_recorded",
            source_device="alexa_echo_show_8",
            payload={
                "topic": "Garden Tomato Plants",
                "participants": ["Arthur", "Ravi"],
                "summary": "Ravi agreed to bring tomato seedlings today at 4:00 PM."
            },
            occurred_at=datetime.now(timezone.utc) - timedelta(hours=22)
        )

        await repo.create_event(
            event_type="object_detected",
            source_device="living_room_cam",
            payload={
                "object": "Reading Glasses",
                "location": "Living Room Coffee Table",
                "confidence": 0.94
            },
            occurred_at=datetime.now(timezone.utc) - timedelta(minutes=15)
        )

        print("ContextOS Household Memory Graph successfully seeded!")

if __name__ == "__main__":
    asyncio.run(seed_household_graph())
