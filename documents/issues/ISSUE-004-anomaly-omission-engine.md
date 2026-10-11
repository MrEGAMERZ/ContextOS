# Issue #4: Anomaly & Omission Engine + Simulated Event Injector

**Status:** Queued  
**Shipment:** Shipment 4  
**Labels:** `engine`, `anomaly`, `simulation`, `shipment-4`

## Description
Build the hybrid anomaly and omission detection engine alongside a synthetic event injection API. The anomaly engine combines event-driven SQL rules with a 60-second temporal clock worker to detect missed behavioral patterns (e.g. front door open >30m, missed morning routine). The injector allows deterministic triggering of all demo scenarios.

## Acceptance Criteria
1. Temporal omission background worker running on a 60-second heartbeat.
2. Anomaly detection rules:
   - Door open duration threshold (>30 minutes).
   - Unusual night activity (kitchen motion between 1 AM and 5 AM).
   - Missed daily routine (e.g., medication drawer not opened by 10 AM).
3. Synthetic Event Injector API (`POST /api/events/inject`) supporting predefined scenario triggers:
   - Scenario 1: Visitor Arrival (Doorbell ring -> Sighting -> Entity update).
   - Scenario 2: Object Relocation (Glasses moved from nightstand to living room table).
   - Scenario 3: Safety Risk (Front door left open for 31 minutes).
4. Real-time alert dispatch to the Caregiver Dashboard via Server-Sent Events (SSE).
