# Issue #7: Advanced Anomaly Engine, Omission Rules & Caregiver Daily Briefing

**Status:** Closed  
**Milestone:** Shipment 7 (`v0.7.0-shipment7`)  
**Hackathon Track:** Alexa+ & Caregiver Ambient Intelligence  
**Labels:** `backend`, `anomaly`, `caregiver`, `ai`, `bedrock`

---

## 1. Problem Statement
Section 8 (Use Case D: "Caregiver Summary") and Section 25 (E: "Caregiver Summary") of `IDEA.md` dictate that ContextOS must not overwhelm caregivers with dozens of raw sensor alerts. Instead, it must:
1. Detect safety-critical anomalies beyond simple door duration, specifically:
   - Late-night exterior door opening (23:00–05:00), indicating dementia wandering risk.
   - Prolonged bathroom occupancy with no motion (>45 min), indicating possible fall or distress.
2. Calculate a quantitative, transparent **Autonomy & Safety Score (0–100)** tracking daily routine compliance, social interactions, and environmental safety flags.
3. Automatically synthesize an empathetic 3-bullet daily executive briefing powered by Amazon Bedrock Claude 3.5 Sonnet.

## 2. Requirements & Deliverables
- [x] Extend `AnomalyDetector` in `backend/app/engine/anomaly.py` with:
  - Rule 3: `wandering_nighttime_door_opened` (late-night door check with HIGH severity alert).
  - Rule 4: `extended_bathroom_inactivity` (bathroom motion cessation fall detector).
- [x] Create `CaregiverSummaryEngine` in `backend/app/engine/caregiver_summary.py`:
  - `compute_health_metrics()`: Computes Autonomy Score (0–100), medication adherence %, and social interaction counts.
  - `generate_daily_briefing()`: Uses Bedrock Claude 3.5 Sonnet to draft concise, empathetic 3-bullet executive summaries and action items.
- [x] Add demo injection scenarios to `EventInjector` in `backend/app/engine/injector.py`:
  - `wandering_nighttime` (door opened at 02:30 AM).
  - `bathroom_fall` (bathroom occupied for 50 min).
- [x] REST endpoints in `backend/app/engine/router.py`:
  - `GET /api/caregiver/briefing`
  - `GET /api/caregiver/health-score`
  - `POST /api/caregiver/briefing/generate`
- [x] Update `BedrockClient` with `invoke_claude` convenience helper and mock caregiver digest.
- [x] 4 unit and integration tests in `backend/tests/test_advanced_anomalies_summary.py`.

## 3. Verification
- 4/4 Shipment 7 tests pass.
- Entire test suite: 23/23 passing in 0.29s.
