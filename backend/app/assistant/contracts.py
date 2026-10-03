from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Any, Mapping


@dataclass(frozen=True)
class AssistantContext:
    incident_id: str
    category: str
    risk_score: float
    risk_level: str
    confidence: float
    indicators: tuple[str, ...] = ()
    xai_summary: str = ""
    incident_status: str = "UNKNOWN"
    recommended_actions: tuple[str, ...] = ()
    security_context: Mapping[str, Any] = field(default_factory=dict)

    @property
    def explanation(self) -> str:
        """Backward-compatible access to the XAI explanation."""
        return self.xai_summary


@dataclass(frozen=True)
class AssistantResponse:
    message: str
    evidence: tuple[str, ...] = ()
    requires_approval: bool = False
    safe: bool = True
    provider: str = "fallback"


@dataclass(frozen=True)
class AssistantConversation:
    id: str
    created_at: datetime
    threat_context: str


@dataclass(frozen=True)
class AssistantMessage:
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime


@dataclass(frozen=True)
class ApprovalRequest:
    response_id: str
    incident_id: str
    action: str
    reason: str
    state: str
    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
