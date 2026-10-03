from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid5, NAMESPACE_URL

from app.notifications.contracts import NotificationEvent, NotificationKind
from app.notifications.service import NotificationService


assistant_notification_service = NotificationService()


def _to_uuid(value: str) -> UUID:
    """
    Convert an arbitrary identifier into a stable UUID.

    Real UUID strings are preserved. Non-UUID identifiers are
    deterministically converted so the notification contract remains valid.
    """
    try:
        return UUID(value)
    except (ValueError, AttributeError):
        return uuid5(NAMESPACE_URL, f"cyberguard:{value}")


def notify_response_approval_required(
    incident_id: str,
    category: str,
    action: str,
    reason: str,
    recipient: str = "security_admin",
) -> NotificationEvent:
    event = NotificationEvent(
        recipient_id=_to_uuid(recipient),
        context_id=_to_uuid(incident_id),
        kind=NotificationKind.SECURITY_RECOMMENDATION,
        title="Response approval required",
        body=(
            f"Incident {incident_id} requires approval for the "
            f"{category} response action: {action}. "
            f"Reason: {reason}"
        ),
        occurred_at=datetime.now(UTC),
        incident_id=_to_uuid(incident_id),
    )

    assistant_notification_service.enqueue(event)
    return event
