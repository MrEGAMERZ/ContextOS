# Issue #8: Permission Boundary Model & Enhanced Agent Tool-Calling Runtime

**Status:** Closed  
**Milestone:** Shipment 8 (`v0.8.0-shipment8`)  
**Hackathon Track:** AWS Builder & AI Safety  
**Labels:** `backend`, `ai`, `safety`, `permissions`, `bedrock`

---

## 1. Problem Statement
Section 15 ("Agent Core") and Section 16 ("Permission Model") of `IDEA.md` specify:
> "The agent should not automatically act simply because an LLM generated an action. Actions pass through: 1. Tool validation, 2. Permission checks, 3. Confidence thresholds, 4. Confirmation requirements."
> "ContextOS distinguishes between: READ, SUGGEST, CONFIRM, ACT, ESCALATE."

Without safety boundaries, an AI agent could hallucinate destructive mutations (like unlocking exterior doors or dismissing medical alerts). ContextOS requires a deterministic PermissionGate that blocks unconfirmed physical mutations, facilitates human-in-the-loop approvals, and manages emergency escalations.

## 2. Requirements & Deliverables
- [x] Create `PermissionGate` in `backend/app/ai/permissions.py`:
  - 5-level enum: `READ`, `SUGGEST`, `CONFIRM`, `ACT`, `ESCALATE`.
  - Configurable action policy mapping (e.g. `query_memory_graph` -> READ, `lock_door` -> CONFIRM, `notify_emergency_contact` -> ESCALATE).
  - In-memory confirmation registry producing cryptographically random confirmation tokens.
  - Broadcasts `CONFIRMATION_REQUIRED`, `CONFIRMATION_RESOLVED`, and `EMERGENCY_ESCALATION` events over SSE.
- [x] AWS credentials validation method `verify_aws_credentials()` in `BedrockClient`:
  - Checks AWS IAM credentials against Bedrock runtime and reports active model IDs and fallback state.
- [x] REST endpoints in `backend/app/ai/router.py`:
  - `GET /api/agent/permissions`: Returns active safety policy mapping.
  - `POST /api/agent/actions/evaluate`: Evaluates an AI-proposed action against the policy matrix.
  - `GET /api/agent/confirmations/pending`: Lists all actions awaiting caregiver/user confirmation.
  - `POST /api/agent/confirmations/{token}/resolve`: Approves or rejects a pending action.
  - `GET /api/agent/aws-status`: Real-time AWS Bedrock connection health.
- [x] 4 unit and integration tests in `backend/tests/test_permissions_agent.py`.

## 3. Verification
- 4/4 Shipment 8 tests pass.
- Entire test suite: 27/27 passing in 0.29s.
