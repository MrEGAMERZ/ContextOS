# PR #4: Anomaly & Omission Engine + Simulated Event Injector

**Branch:** `feat/shipment-4-anomaly-event-injector` -> `main`  
**Shipment:** Shipment 4 (`v0.4.0-shipment4`)  
**Status:** Merged  
**Related Issue:** #4 ([documents/issues/ISSUE-004-anomaly-omission-engine.md](../issues/ISSUE-004-anomaly-omission-engine.md))

## Summary
Implements the hybrid anomaly and omission detection engine with 60-second temporal clock rules, deep reasoning triggers on Amazon Bedrock, real-time Server-Sent Events (SSE) broadcasting, and the web-based Simulated Event Injector for fail-safe hackathon demonstrations.

## Changes
- **Anomaly & Omission Detector (`backend/app/engine/anomaly.py`)**:
  - Door Open Duration Rule: Evaluates state changes and triggers an omission alert if any entrance door remains open beyond 30 minutes.
  - Missed Routine Rule: Detects unfulfilled medication or meal windows and generates health routine omission warnings.
  - Automatic CoT Reasoning Trigger: Seamlessly invokes Bedrock Claude 3.5 Sonnet to produce step-by-step `<thinking>` logs and recommended caregiver actions.
- **SSE Event Broadcaster (`backend/app/engine/stream.py`)**:
  - High-concurrency async SSE broadcaster publishing live events and anomalies to web clients at `GET /api/events/stream`.
- **Simulated Event Injector (`backend/app/engine/injector.py`, `backend/app/engine/router.py`)**:
  - `POST /api/events/inject`: One-click scenario triggers:
    1. `visitor_arrival`: Neighbor Ravi at front porch with garden seedling context.
    2. `object_relocation`: Reading glasses relocated to Kitchen Counter.
    3. `front_door_open_anomaly`: Door left open for 35 minutes triggering safety omission.
    4. `missed_medication`: Morning medication omitted past schedule.
  - `POST /api/engine/tick`: Manual temporal clock execution trigger.
- **Pytest Suite (`backend/tests/test_anomaly_injector.py`)**:
  - Tests covering visitor injection, door open omission, missed medication, and SSE message broadcast.

## Test Verification
- All 14 tests pass across the entire platform in `0.17s`.
