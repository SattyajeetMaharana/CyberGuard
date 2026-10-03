from uuid import uuid4

from .contracts import (
    Notification,
    NotificationEvent,
    NotificationType,
)


class NotificationService:
    def __init__(self):
        self._events: dict[str, NotificationEvent] = {}

    def enqueue(self, event: NotificationEvent) -> str:
        tracking_id = str(uuid4())
        self._events[tracking_id] = event
        return tracking_id

    def get(self, tracking_id: str) -> NotificationEvent | None:
        return self._events.get(tracking_id)


notification_service = NotificationService()


def create_notification(
    user_id: str,
    notification_type: NotificationType,
    title: str,
    message: str,
) -> Notification:
    """Backward-compatible notification creation API."""

    return Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
    )