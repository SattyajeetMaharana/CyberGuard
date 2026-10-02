from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class PolicyDecision(StrEnum):
    ALLOW = "ALLOW"
    REQUIRE_ADMIN_REVIEW = "REQUIRE_ADMIN_REVIEW"
    REQUIRE_USER_CONFIRMATION = "REQUIRE_USER_CONFIRMATION"
    DENY = "DENY"


@dataclass(frozen=True)
class PolicyContext:
    risk_score: float
    confidence: float
    category: str
    user_context: str
    organization_policy: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyEvaluation:
    decision: PolicyDecision
    reason: str
    policy_version: str | None = None