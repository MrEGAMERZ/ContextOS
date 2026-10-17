"""Permission and Safety Boundary Enforcement Layer for ContextOS.

Implements the formal 5-level permission model specified in IDEA.md Section 16:
- READ: May retrieve context (always allowed).
- SUGGEST: May recommend an action to user/caregiver.
- CONFIRM: Requires explicit confirmation before execution (e.g. locking door, cancelling alert).
- ACT: Predefined authorized automatic execution.
- ESCALATE: Automatically dispatches notifications to trusted contacts under critical conditions.
"""

from enum import Enum
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.engine.stream import broadcaster


class PermissionLevel(str, Enum):
    READ = "read"
    SUGGEST = "suggest"
    CONFIRM = "confirm"
    ACT = "act"
    ESCALATE = "escalate"


class ActionRequest(BaseModel):
    action_type: str = Field(..., description="Action name, e.g. lock_door, query_context, escalate_caregiver")
    target_entity: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    reasoning: Optional[str] = None


class PermissionDecision(BaseModel):
    action_type: str
    required_level: PermissionLevel
    allowed: bool
    status: str  # EXECUTED, SUGGESTED, PENDING_CONFIRMATION, ESCALATED, DENIED
    confirmation_token: Optional[str] = None
    message: str
    timestamp: str


class PendingConfirmation(BaseModel):
    confirmation_token: str
    action_type: str
    target_entity: Optional[str]
    parameters: Dict[str, Any]
    reasoning: Optional[str]
    created_at: str
    status: str = "pending"  # pending, approved, rejected


class PermissionGate:
    """Central authority evaluating all AI-proposed actions before smart-home execution."""

    DEFAULT_POLICY: Dict[str, PermissionLevel] = {
        # READ
        "query_memory_graph": PermissionLevel.READ,
        "get_entity_context": PermissionLevel.READ,
        "get_recent_events": PermissionLevel.READ,
        "locate_object": PermissionLevel.READ,
        # SUGGEST
        "suggest_routine_schedule": PermissionLevel.SUGGEST,
        "recommend_medication_window": PermissionLevel.SUGGEST,
        "suggest_call_relative": PermissionLevel.SUGGEST,
        # CONFIRM (Safety-critical mutations require human in the loop)
        "lock_door": PermissionLevel.CONFIRM,
        "unlock_door": PermissionLevel.CONFIRM,
        "adjust_thermostat": PermissionLevel.CONFIRM,
        "dismiss_critical_anomaly": PermissionLevel.CONFIRM,
        # ACT (Pre-approved safe actions)
        "log_audit_entry": PermissionLevel.ACT,
        "refresh_device_status": PermissionLevel.ACT,
        "update_last_seen_time": PermissionLevel.ACT,
        # ESCALATE
        "notify_emergency_contact": PermissionLevel.ESCALATE,
        "dispatch_caregiver_alert": PermissionLevel.ESCALATE,
        "report_wandering_risk": PermissionLevel.ESCALATE,
    }

    def __init__(self):
        self._policy = dict(self.DEFAULT_POLICY)
        self._pending: Dict[str, PendingConfirmation] = {}

    def get_policy(self) -> Dict[str, str]:
        return {k: v.value for k, v in self._policy.items()}

    def get_pending_confirmations(self) -> List[PendingConfirmation]:
        return [c for c in self._pending.values() if c.status == "pending"]

    async def evaluate_action(self, request: ActionRequest) -> PermissionDecision:
        now_iso = datetime.now(timezone.utc).isoformat()
        required_level = self._policy.get(request.action_type, PermissionLevel.CONFIRM)

        if required_level == PermissionLevel.READ:
            return PermissionDecision(
                action_type=request.action_type,
                required_level=required_level,
                allowed=True,
                status="EXECUTED",
                message=f"Action '{request.action_type}' authorized under READ permission.",
                timestamp=now_iso
            )

        elif required_level == PermissionLevel.SUGGEST:
            return PermissionDecision(
                action_type=request.action_type,
                required_level=required_level,
                allowed=True,
                status="SUGGESTED",
                message=f"Action '{request.action_type}' proposed as a non-intrusive suggestion.",
                timestamp=now_iso
            )

        elif required_level == PermissionLevel.CONFIRM:
            token = f"conf_{uuid.uuid4().hex[:12]}"
            pending = PendingConfirmation(
                confirmation_token=token,
                action_type=request.action_type,
                target_entity=request.target_entity,
                parameters=request.parameters,
                reasoning=request.reasoning,
                created_at=now_iso,
                status="pending"
            )
            self._pending[token] = pending

            # Broadcast confirmation request to caregiver UI
            await broadcaster.broadcast({
                "type": "CONFIRMATION_REQUIRED",
                "confirmation_token": token,
                "action_type": request.action_type,
                "target_entity": request.target_entity,
                "reasoning": request.reasoning,
                "created_at": now_iso
            })

            return PermissionDecision(
                action_type=request.action_type,
                required_level=required_level,
                allowed=False,
                status="PENDING_CONFIRMATION",
                confirmation_token=token,
                message=f"Action '{request.action_type}' requires explicit caregiver confirmation. Token: {token}",
                timestamp=now_iso
            )

        elif required_level == PermissionLevel.ACT:
            return PermissionDecision(
                action_type=request.action_type,
                required_level=required_level,
                allowed=True,
                status="EXECUTED",
                message=f"Action '{request.action_type}' executed autonomously under authorized ACT permission.",
                timestamp=now_iso
            )

        elif required_level == PermissionLevel.ESCALATE:
            # Broadcast escalation alert immediately
            await broadcaster.broadcast({
                "type": "EMERGENCY_ESCALATION",
                "action_type": request.action_type,
                "target_entity": request.target_entity,
                "reasoning": request.reasoning,
                "priority": "HIGH",
                "timestamp": now_iso
            })

            return PermissionDecision(
                action_type=request.action_type,
                required_level=required_level,
                allowed=True,
                status="ESCALATED",
                message=f"Critical Action '{request.action_type}' escalated to emergency caregiver contacts.",
                timestamp=now_iso
            )

        return PermissionDecision(
            action_type=request.action_type,
            required_level=PermissionLevel.CONFIRM,
            allowed=False,
            status="DENIED",
            message="Unknown permission policy level.",
            timestamp=now_iso
        )

    async def resolve_confirmation(self, token: str, approved: bool) -> Dict[str, Any]:
        """User or caregiver approves/rejects a pending confirmation."""
        pending = self._pending.get(token)
        if not pending:
            return {"status": "error", "message": f"Confirmation token '{token}' not found or expired."}

        if pending.status != "pending":
            return {"status": "error", "message": f"Token '{token}' has already been {pending.status}."}

        pending.status = "approved" if approved else "rejected"
        now_iso = datetime.now(timezone.utc).isoformat()

        await broadcaster.broadcast({
            "type": "CONFIRMATION_RESOLVED",
            "confirmation_token": token,
            "status": pending.status,
            "action_type": pending.action_type,
            "timestamp": now_iso
        })

        return {
            "status": "success",
            "confirmation_token": token,
            "decision": pending.status,
            "action_type": pending.action_type,
            "executed": approved,
            "resolved_at": now_iso
        }


permission_gate = PermissionGate()
