from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping, Protocol, Sequence


class ResponseAction(StrEnum):
    REVOKE_SESSION = "revoke_session"
    SUSPEND_DEVICE = "suspend_device"
    REQUIRE_PASSWORD_RESET = "require_password_reset"
    NOTIFY_ADMIN = "notify_admin"
    REQUEST_USER_CONFIRMATION = "request_user_confirmation"


@dataclass(frozen=True)
class ResponseRecommendation:
    action: ResponseAction
    reason: str
    requires_approval: bool = True
    parameters: Mapping[str, Any] = field(default_factory=dict)


class ResponseRecommender(Protocol):
    def recommend(
        self,
        *,
        policy_result: object,
        detection: object,
    ) -> Sequence[ResponseRecommendation]:
        """Return proposed actions; do not execute them."""
        ...