import time
import json
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.repository.graph_repo import GraphRepository
from app.mcp.server import MCPServer
from app.ai.bedrock_client import BedrockClient

SYSTEM_PROMPT_VOICE = """You are ContextOS, an ambient, context-aware AI assistant helping Arthur live independently.
Arthur is 78 years old. Be clear, calm, reassuring, and concise (<2 sentences).
Always provide your step-by-step reasoning inside <thinking>...</thinking> tags before giving your final response.
Explain WHO someone is, WHY they are there, or WHERE something is located based on the home's memory graph."""

SYSTEM_PROMPT_DEEP = """You are ContextOS Deep Reasoning Core running on Amazon Bedrock (Claude 3.5 Sonnet).
Your job is to analyze smart home event subgraphs, detect behavioral patterns, explain omissions, and provide caregiver insights.
You must think rigorously step-by-step inside <thinking>...</thinking> tags before formulating conclusions.
Assess whether situations require caregiver escalation or are normal daily routines."""

class ContextOSAgent:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = GraphRepository(session)
        self.mcp = MCPServer(session)
        self.bedrock = BedrockClient()

    async def answer_voice_query(self, query: str) -> Dict[str, Any]:
        """
        Fast Conversational Voice Query Pipeline (<1.5s total time).
        1. Queries local Memory Graph via MCP (<5ms).
        2. Formats prompt with graph context.
        3. Calls Bedrock Claude 3.5 Haiku.
        4. Logs full <thinking> reasoning into action_audit_logs.
        """
        start_time = time.perf_counter()

        # Step 1: Rapid MCP Context Lookup
        mcp_result = await self.mcp.execute_tool("query_memory_graph", {"query": query})
        matches = mcp_result.get("data", {}).get("matches", [])
        
        context_data = {}
        if matches:
            top_entity = matches[0]["name"]
            entity_context = await self.mcp.execute_tool("get_entity_context", {"entity_name": top_entity})
            context_data = entity_context.get("data", {})

        # Step 2: Build Grounded Prompt
        prompt = (
            f"User Voice Query: \"{query}\"\n\n"
            f"ContextOS Memory Graph Context:\n"
            f"{json.dumps(context_data, indent=2)}\n\n"
            f"Answer Arthur's question directly, accurately, and reassuringly."
        )

        # Step 3: Bedrock Invocation
        thinking, response = await self.bedrock.invoke_model(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_VOICE,
            model_id=settings.BEDROCK_MODEL_ID_FAST,
            max_tokens=300,
            temperature=0.1
        )

        # Step 4: Persist in Action Audit Logs
        audit_log = await self.repo.log_action(
            action_type="alexa_voice_turn",
            prompt_context=prompt,
            thinking_process=thinking,
            output_response=response
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "query": query,
            "response": response,
            "thinking_process": thinking,
            "audit_id": audit_log.id,
            "execution_ms": elapsed_ms,
            "model_used": settings.BEDROCK_MODEL_ID_FAST,
            "grounded_entity": matches[0]["name"] if matches else None
        }

    async def deep_reasoning_inference(
        self,
        event_id: Optional[str],
        topic: str,
        context_subgraph: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Asynchronous Deep Reasoning Pipeline using Claude 3.5 Sonnet.
        Analyzes subgraphs, evaluates potential anomalies, and logs CoT steps.
        """
        start_time = time.perf_counter()

        prompt = (
            f"Topic: {topic}\n"
            f"Event Subgraph:\n{json.dumps(context_subgraph, indent=2)}\n\n"
            f"Analyze this situation. Identify potential anomalies or omissions. "
            f"State whether escalation to caregiver is required."
        )

        thinking, response = await self.bedrock.invoke_model(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_DEEP,
            model_id=settings.BEDROCK_MODEL_ID_DEEP,
            max_tokens=800,
            temperature=0.2
        )

        audit_log = await self.repo.log_action(
            action_type="deep_reasoning_analysis",
            trigger_event_id=event_id,
            prompt_context=prompt,
            thinking_process=thinking,
            output_response=response
        )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "topic": topic,
            "analysis": response,
            "thinking_process": thinking,
            "audit_id": audit_log.id,
            "execution_ms": elapsed_ms,
            "model_used": settings.BEDROCK_MODEL_ID_DEEP
        }
