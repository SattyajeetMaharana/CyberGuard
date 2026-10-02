from uuid import uuid4

from .contracts import NotificationEvent


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