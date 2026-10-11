# PR #3: Dual-Tier Bedrock Agent & Chain-of-Thought (CoT) Engine

**Branch:** `feat/shipment-3-bedrock-reasoning` -> `main`  
**Shipment:** Shipment 3 (`v0.3.0-shipment3`)  
**Status:** Merged  
**Related Issue:** #3 ([documents/issues/ISSUE-003-bedrock-dual-tier-agent.md](../issues/ISSUE-003-bedrock-dual-tier-agent.md))

## Summary
Integrates Amazon Bedrock with a dual-tier model architecture (Claude 3.5 Haiku for rapid conversational speech turns; Claude 3.5 Sonnet for deep multi-hop reasoning), structured `<thinking>` XML extraction, transparent local mock fallback, and action audit trail persistence for the "Why Did You Do That?" UI drawer.

## Changes
- **Bedrock Client (`backend/app/ai/bedrock_client.py`)**:
  - AWS Bedrock Converse API integration supporting region and credential configuration.
  - Regex parser isolating `<thinking>` Chain of Thought blocks from the customer-facing response.
  - High-fidelity Bedrock Claude 3.5 simulator mode enabling 100% offline development, testing, and judge demonstrations without AWS billing dependencies.
- **Dual-Tier Agent (`backend/app/ai/agent.py`)**:
  - `answer_voice_query()`: Rapid pipeline for conversational speech turns utilizing MCP graph tools to retrieve immediate context in <5ms, invoking Claude 3.5 Haiku, and logging the reasoning audit record.
  - `deep_reasoning_inference()`: Background pipeline invoking Claude 3.5 Sonnet on complex event subgraphs, evaluating potential anomalies and caregiver escalation policies.
- **REST Surface (`backend/app/ai/router.py`)**:
  - `POST /api/agent/query`: Natural language conversational query endpoint.
  - `GET /api/audit/{audit_id}`: Inspectable audit record endpoint returning the exact `<thinking>` process for UI display.
- **Pytest Suite (`backend/tests/test_bedrock_reasoning.py`)**:
  - Automated tests for `<thinking>` tag extraction, conversational question answering, audit trail retrieval, and deep reasoning analysis.

## Test Verification
- All 10 tests pass across the entire codebase in `0.12s`.
- Both fast conversational queries and deep inference properly extract `<thinking>` rationale and persist them to `action_audit_logs`.
