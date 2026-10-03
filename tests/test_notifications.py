from app.notifications.contracts import NotificationType
from app.notifications.service import create_notification


def test_notification_creation():
    notification = create_notification(
        "U001",
        NotificationType.THREAT,
        "Threat detected",
        "A high-risk threat was detected."
    )

    assert notification.user_id == "U001"
    assert notification.notification_type == NotificationType.THREAT