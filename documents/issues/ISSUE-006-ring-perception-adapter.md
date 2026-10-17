# Issue #6: Ring Doorbell & Camera Perception Adapter

**Status:** Closed  
**Milestone:** Shipment 6 (`v0.6.0-shipment6`)  
**Hackathon Track:** Ring Track & Alexa+ Perception  
**Labels:** `backend`, `ring`, `perception`, `hardware-adapter`

---

## 1. Problem Statement
`IDEA.md` (Sections 19 and 52) specifies that while Alexa+ is our primary voice track, Ring naturally supplies environmental contextual events. In traditional smart homes, Ring only outputs disconnected signals like "Motion detected" or "Doorbell chime pressed". For an ambient elderly care assistant, ContextOS must ingest these raw video doorbell events and translate them into human-meaningful knowledge graph updates (e.g. "Ravi, your neighbor, arrived at Front Door. Ring Doorbell pressed").

## 2. Requirements & Deliverables
- [x] Create `RingAdapter` in `backend/app/adapters/ring_adapter.py`.
- [x] Pydantic models for incoming Ring webhooks (`RingWebhookPayload`) and simulation requests (`RingSimulationRequest`).
- [x] Automatically sync/register Ring hardware devices into the Memory Graph entity registry with battery levels and firmware ping timestamps.
- [x] Transform Ring dings and motion detections into canonical ContextOS events (`doorbell_rung`, `person_detected`, `motion_detected`).
- [x] Contextual threat level assignment (LOW for expected neighbors, MEDIUM for unidentified visitors, HIGH for late-night motion between 23:00 and 05:00).
- [x] Broadcast live Ring perception updates over Server-Sent Events (`broadcaster.broadcast`).
- [x] FastAPI router in `backend/app/adapters/router.py`:
  - `POST /api/ring/webhook`
  - `POST /api/ring/simulate`
  - `GET /api/ring/devices`
  - `GET /api/ring/recent`
- [x] Mount Ring router in `backend/app/main.py`.
- [x] 4 comprehensive unit and integration tests in `backend/tests/test_ring_adapter.py`.

## 3. Verification
- 4/4 Ring adapter tests passing (`test_ring_webhook_ding_neighbor`, `test_ring_webhook_late_night_motion`, `test_ring_simulate_endpoint`, `test_ring_devices_and_recent_endpoints`).
- Total test suite: 19/19 passing in 0.22s.
