# ContextOS — Developer Friction Log & Engineering Learnings

> **Document Purpose**: Real-world friction log and technical retrospective compiled during the development of ContextOS for the Amazon Developer Hackathon (Alexa+, Ring, and AWS Bedrock tracks).

---

## 1. Alexa+ Model Context Protocol (MCP) Latency SLA

### The Friction:
Alexa voice interactions enforce a strict ~8-second total speech turnaround budget before voice session timeout or conversational failure. When integrating LLMs with external tools:
- Standard cloud LLM latency for tool selection + JSON generation: **1,200ms – 2,500ms**
- Tool execution: **200ms – 600ms**
- Second LLM synthesis turn for final response: **1,500ms – 3,000ms**
- Alexa TTS audio generation & streaming: **800ms – 1,200ms**
- **Total Latency**: Often exceeding **6,000ms – 7,500ms**, teetering on the edge of conversational failure.

### The Resolution in ContextOS:
We decoupled the **Voice Path** from the **Deep Reasoning Path**:
1. Built a **deterministic 2-hop relational SQL graph traversal** in the self-hosted MCP server (`query_memory_graph`, `get_entity_context`).
2. Optimized queries to execute in pure compiled SQLite/PostgreSQL, returning pre-formatted contextual summaries in **< 35ms**.
3. For voice queries like *"Who is at the door?"*, the MCP server provides direct, factual grounding directly to Alexa or Claude 3.5 Haiku, bypassing multi-step chain-of-thought loops on the hot voice path.
4. Deep chain-of-thought reasoning (Claude 3.5 Sonnet) is reserved for asynchronous anomaly detection, caregiver briefings, and safety evaluations where latency budgets are relaxed.

---

## 2. Amazon Bedrock Converse API: `<thinking>` Tag Separation

### The Friction:
When prompting Amazon Bedrock models (such as Claude 3.5 Sonnet) to employ Chain of Thought reasoning, the model emits internal deliberation tags: `<thinking>...</thinking>`.
If passed directly into voice interfaces or standard notifications:
1. Alexa's Text-to-Speech (TTS) engine attempts to read internal reasoning aloud: *"Less-than thinking Arthur is prone to forgetting his morning pills greater-than..."*, resulting in a terrible user experience.
2. In caregiver dashboards, raw unparsed tokens look like unstructured text dump rather than an auditable explanation.

### The Resolution in ContextOS:
We built an explicit parser in `backend/app/ai/bedrock_client.py`:
- Uses regex isolation `re.search(r"<thinking>(.*?)</thinking>", raw_content, re.DOTALL)` to cleanly separate the **reasoning trace** from the **customer-facing response**.
- Persists the reasoning trace into an immutable `action_audit_logs` table under `thought_process`.
- The frontend exposes this through a dedicated slide-out drawer: **"Why Did You Do That?" (CoT Inspector)**.
- Voice endpoints receive only clean, sanitized text with all thinking tags stripped.

---

## 3. SQLAlchemy 2.0 Async JSON Column Dirty Tracking

### The Friction:
In `backend/app/db/models.py`, `Entity` and `Event` models store flexible attributes in a `JSON` column (`metadata_`).
During event ingestion, updating a nested dictionary key in place:
```python
# FAILS SILENTLY:
entity.metadata_["last_seen"] = timestamp
session.add(entity)
await session.commit()
```
SQLAlchemy 2.0 async sessions do not detect in-place dictionary mutations because the object identity of the dictionary does not change. As a result, the changes were never flushed to the database, causing state sync bugs between Ring events and the memory graph.

### The Resolution in ContextOS:
Enforced an immutable dictionary assignment pattern across all service layers:
```python
# WORKS RELIABLY:
new_metadata = dict(entity.metadata_ or {})
new_metadata["last_seen"] = timestamp
entity.metadata_ = new_metadata
```
This guarantees that SQLAlchemy's unit-of-work tracks the change as a dirty attribute and issues the proper SQL `UPDATE` statement.

---

## 4. Ring Perception Webhook Normalization & Debouncing

### The Friction:
Real Ring devices often send a barrage of webhook notifications in rapid succession:
- A single visitor can trigger a motion event, followed 2 seconds later by a ding event, followed by multiple zone update events.
- Ingesting every webhook as an isolated graph node flooded the knowledge graph with duplicate entity edges (`Arthur -> visited_by -> UnknownVisitor` x 4).

### The Resolution in ContextOS:
Implemented a 10-second deduplication and debounce window in `backend/app/adapters/ring_adapter.py`:
- Events within the same sliding window for the same device ID are merged into an active session.
- Only the highest severity threat tier (`DING` > `MOTION`) updates the primary graph state.
- Maintains device battery level and signal strength in a synchronized `ring_devices` registry.

---

## 5. GitHub Personal Access Token (PAT) Workflow Scope Limitations

### The Friction:
When configuring the CI/CD pipeline, standard GitHub actions workflows live in `.github/workflows/ci.yml`. However, developer PATs generated without the explicit `workflow` OAuth scope fail with:
`fatal: refusing to allow a Personal Access Token to create or update workflow without workflow scope`.

### The Resolution in ContextOS:
To guarantee non-destructive, reproducible CI verification across all developer environments:
1. Created an enterprise-ready pipeline manifest in `ci/ci.yml`.
2. Documented exact deployment steps with Docker Compose (`backend`, `frontend`, `caching`, and `database`) so the complete build and test suite can be run locally or in any runner with a single command:
   ```bash
   docker compose up --build -d
   ```
3. Created standalone pytest verification scripts and test harnesses that execute in <0.3s without external API dependencies.

---

## 6. Web Speech API Autoplay Policies & Audio Hydration

### The Friction:
In modern web browsers (Chrome, Safari, Edge), the `window.speechSynthesis` API is strictly subject to browser Autoplay policies. Attempting to trigger spoken responses automatically upon receiving an SSE event fails silently if the user has not interacted with the DOM.

### The Resolution in ContextOS:
In `frontend/components/VoiceHarness.tsx`:
- Bound audio synthesis to explicit user interaction ("Test Voice Query" button or "Speak" toggle).
- Added a visual animated soundwave indicator and a fallback text display with copyable transcript, guaranteeing accessibility even when browser audio is muted.
