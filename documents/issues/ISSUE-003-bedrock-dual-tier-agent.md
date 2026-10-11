# Issue #3: Dual-Tier Bedrock Agent & Chain-of-Thought Engine

**Status:** Closed (Resolved by [PR #3](../pull_requests/PR-003-bedrock-dual-tier-agent.md))  
**Shipment:** Shipment 3  
**Labels:** `bedrock`, `ai`, `cot`, `aws-builder`, `shipment-3`

## Description
Integrate AWS Bedrock using a dual-tier model strategy. Lightweight models handle prompt synthesis for conversational voice turns, while Claude 3.5 Sonnet operates asynchronously in the background to infer complex contextual relationships, generate `<thinking>` Chain of Thought (CoT) reasoning logs, and persist them in `action_audit_logs`.

## Acceptance Criteria
1. Bedrock client wrapper supporting AWS Bedrock Converse API with region and credential configuration.
2. Dual-tier routing:
   - Synchronous voice synthesis: Claude 3.5 Haiku / lightweight model with strict token limits (<250 tokens).
   - Asynchronous deep reasoning: Claude 3.5 Sonnet analyzing multi-hop entity subgraphs.
3. Structured `<thinking>` tag enforcement in system prompts and regex/parser extraction into `action_audit_logs.thinking_process`.
4. Endpoint `GET /api/audit/{action_id}` exposing the exact chain of thought for the "Why did you do that?" UI drawer.
5. Mock Bedrock mode for local testing without active AWS billing / credentials.
