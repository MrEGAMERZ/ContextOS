import re
import os
from typing import Tuple, Dict, Any, Optional
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from app.config import settings

class BedrockClient:
    def __init__(self):
        self.region = settings.AWS_REGION
        self.mock_mode = settings.MOCK_BEDROCK
        self._client = None

        if not self.mock_mode and settings.AWS_ACCESS_KEY_ID:
            try:
                self._client = boto3.client(
                    service_name="bedrock-runtime",
                    region_name=self.region,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
            except Exception:
                self.mock_mode = True

    @staticmethod
    def extract_thinking_and_response(raw_text: str) -> Tuple[str, str]:
        """
        Extracts <thinking>...</thinking> XML block from model generation.
        Returns (thinking_process, clean_response).
        """
        match = re.search(r"<thinking>(.*?)</thinking>", raw_text, flags=re.DOTALL | re.IGNORECASE)
        if match:
            thinking = match.group(1).strip()
            clean_response = re.sub(r"<thinking>.*?</thinking>", "", raw_text, flags=re.DOTALL | re.IGNORECASE).strip()
            return thinking, clean_response
        return "Direct inference (no explicit thinking block generated).", raw_text.strip()

    async def invoke_model(
        self,
        prompt: str,
        system_prompt: str,
        model_id: str,
        max_tokens: int = 1000,
        temperature: float = 0.2
    ) -> Tuple[str, str]:
        """
        Invokes Claude on Amazon Bedrock. Returns (thinking_process, clean_response).
        """
        if self.mock_mode or not self._client:
            return self._mock_bedrock_response(prompt, system_prompt, model_id)

        try:
            response = self._client.converse(
                modelId=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                system=[{"text": system_prompt}],
                inferenceConfig={
                    "maxTokens": max_tokens,
                    "temperature": temperature
                }
            )
            raw_text = response["output"]["message"]["content"][0]["text"]
            return self.extract_thinking_and_response(raw_text)
        except (BotoCoreError, ClientError, Exception) as e:
            # Resilient fallback to mock mode if AWS is unreachable
            return self._mock_bedrock_response(prompt, system_prompt, model_id, fallback_reason=str(e))

    def _mock_bedrock_response(
        self,
        prompt: str,
        system_prompt: str,
        model_id: str,
        fallback_reason: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        High-fidelity Bedrock Claude 3.5 simulator for local tests, hackathon demos, and zero-dependency runs.
        """
        prompt_lower = prompt.lower()

        if "anomaly" in prompt_lower or "omission" in prompt_lower or "left open" in prompt_lower or "duration" in prompt_lower:
            thinking = (
                "1. State Evaluation: Front door has been open for 31 minutes.\n"
                "2. Pattern Comparison: Routine door open duration is < 3 minutes.\n"
                "3. Risk Level: Elevated safety risk for independent living.\n"
                "4. Escalation Policy: Trigger notification to caregiver Sarah."
            )
            response = (
                "Notice: The front door has been left open for over 30 minutes with no motion detected outside. "
                "Recommended action: send quiet check-in notification to caregiver Sarah."
            )
        elif "who is" in prompt_lower or "doorbell" in prompt_lower or "visitor" in prompt_lower or "ravi" in prompt_lower or "door" in prompt_lower:
            thinking = (
                "1. Entity Resolution: Received query about front door / visitor.\n"
                "2. Context Retrieval: Identified entity 'Ravi' (neighbor) and 'Front Porch'.\n"
                "3. Relational Verification: Ravi spoke with Arthur yesterday about tomato plants and scheduled a visit for 4 PM.\n"
                "4. Confidence Evaluation: Confidence 0.98; known trusted neighbor.\n"
                "5. Action: Formulate clear, calming answer confirming identity, relationship, and scheduled reason."
            )
            response = (
                "That's your neighbor Ravi. You spoke with him yesterday about the garden tomato plants, "
                "and he was expected to visit around 4:00 PM."
            )
        elif "glasses" in prompt_lower or "where" in prompt_lower:
            thinking = (
                "1. Entity Resolution: Target object is 'Reading Glasses'.\n"
                "2. Location Lookup: Sighting event 15 minutes ago by living room camera.\n"
                "3. Edge Traversal: Reading Glasses -> located_in -> Living Room Table (weight: 0.94).\n"
                "4. Temporal Recency: Last seen ~15 minutes ago.\n"
                "5. Action: Report precise location and confidence."
            )
            response = "Your reading glasses were last seen on the living room table about 15 minutes ago."
        elif "caregiver" in prompt_lower or "briefing" in prompt_lower or "autonomy" in prompt_lower:
            thinking = (
                "1. Data Aggregation: Analyzed last 24h event history and routine states.\n"
                "2. Adherence Scoring: Evaluated morning medication completion and scheduled time.\n"
                "3. Social Context: Detected neighbor visit from Ravi; healthy social engagement.\n"
                "4. Anomaly Assessment: Minimal safety concerns; synthesized executive summary."
            )
            response = (
                "1. Health & Routine: Arthur completed morning medication on schedule and maintained stable daily activity.\n"
                "2. Social & Environmental: Welcomed neighbor Ravi for a garden conversation; steady daytime mobility.\n"
                "3. Safety & Interventions: Handled minor environmental flags promptly; household state remains peaceful and secure."
            )
        else:
            thinking = (
                f"1. Analyzed query against ContextOS semantic graph.\n"
                f"2. Model tier: {model_id}.\n"
                f"3. Retrieved immediate context nodes and synthesized response."
            )
            response = f"Based on your home's current context, everything appears in order. Query received: '{prompt}'."

        if fallback_reason:
            thinking = f"[Mock Fallback: {fallback_reason}]\n" + thinking

        return thinking, response

    async def invoke_claude(
        self,
        model_tier: str,
        prompt: str,
        system_prompt: str = "You are ContextOS ambient AI.",
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Convenience method accepting tier name ('sonnet' or 'haiku')."""
        if model_tier.lower() == "haiku":
            model_id = settings.BEDROCK_MODEL_ID_FAST
        else:
            model_id = settings.BEDROCK_MODEL_ID_DEEP

        thinking, response = await self.invoke_model(
            prompt=prompt,
            system_prompt=system_prompt,
            model_id=model_id,
            max_tokens=max_tokens
        )
        return {
            "thinking_process": thinking,
            "content": response,
            "model_id": model_id
        }


bedrock_client = BedrockClient()

