# Issue #1: Memory Graph Engine & Database Foundation

**Status:** Open  
**Shipment:** Shipment 1  
**Labels:** `backend`, `database`, `core`, `shipment-1`

## Description
Scaffold the core ContextOS backend and implement the foundational relational Memory Graph schema. The platform needs to store people, objects, locations, and routines as entities, map typed relationships between them with weights and metadata, record raw and contextual events, and persist action audit logs.

## Acceptance Criteria
1. Project structure with modern Python packaging (uv / pip / requirements.txt).
2. Database models for `entities`, `relationships`, `events`, and `action_audit_logs`.
3. Support for SQLite (for seamless local demo/tests) and PostgreSQL (for production AWS RDS / Supabase).
4. Asynchronous Graph Repository providing:
   - Entity CRUD & lookup by name/type
   - Relationship creation and 2-hop neighborhood expansion
   - Event logging with payload & timestamp
   - Querying recent events by entity or type
5. Database seed script providing a rich default household graph (Ravi neighbor, Sarah daughter, front door camera, living room speaker, glasses object, medication routine).
6. Comprehensive test suite achieving 100% pass rate.
