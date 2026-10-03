from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class PolicyDecision(StrEnum):
    ALLOW = "ALLOW"
    REQUIRE_ADMIN_REVIEW = "REQUIRE_ADMIN_REVIEW"
    REQUIRE_USER_CONFIRMATION = "REQUIRE_USER_CONFIRMATION"
    DENY = "DENY"


@dataclass(frozen=True)
class PolicyInput:
    """Backward-compatible input used by the original Policy API."""

    risk_score: float
    confidence: float
    category: str


@dataclass(frozen=True)
class PolicyContext:
    risk_score: float
    confidence: float
    category: str
    user_context: str = ""
    organization_id: str | None = None
    organization_policy: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyEvaluation:
    decision: PolicyDecision
    reason: str
    policy_version: str | None = None
    create_incident: bool = False
    create_alert: bool = False

    @property
    def action(self) -> str:
        """Backward-compatible action name."""
        if self.decision == PolicyDecision.REQUIRE_ADMIN_REVIEW:
            return "review"
        if self.decision == PolicyDecision.REQUIRE_USER_CONFIRMATION:
            return "confirm"
        if self.decision == PolicyDecision.DENY:
            return "deny"
        return "allow"

    @property
    def requires_admin_review(self) -> bool:
        """Backward-compatible admin-review flag."""
        return self.decision == PolicyDecision.REQUIRE_ADMIN_REVIEW


@dataclass(frozen=True)
class SecurityPolicy:
    minimum_risk_score: float = 60
    minimum_confidence: float = 0.0
    create_incident: bool = True
    create_alert: bool = True
    version: str = "v1"