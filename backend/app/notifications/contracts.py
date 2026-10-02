from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class NotificationKind(StrEnum):
    THREAT = "threat"
    INCIDENT = "incident"
    WARNING = "warning"
    SUSPENSION = "suspension"
    SECURITY_RECOMMENDATION = "security_recommendation"


class NotificationChannel(StrEnum):
    IN_APP = "IN_APP"
    PUSH = "PUSH"
    EMAIL = "EMAIL"


@dataclass(frozen=True)
class NotificationEvent:
    recipient_id: UUID
    context_id: UUID
    kind: NotificationKind
    title: str
    body: str
    occurred_at: datetime
    incident_id: UUID | None = None
    detection_id: UUID | None = None


class NotificationService(Protocol):
    def enqueue(self, event: NotificationEvent) -> str:
        """Queue the event and return a tracking ID."""
        ...