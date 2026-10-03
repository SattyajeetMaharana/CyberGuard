from uuid import uuid4

from app.incidents.contracts import IncidentStatus
from app.notifications.service import NotificationService
from app.pipeline.security_pipeline import SecurityPipeline
from app.scoring.service import ScoreService


class MockDetection:
    def __init__(
        self,
        *,
        risk_score,
        confidence,
        category,
        user_id,
        context_id,
        indicators=None,
    ):
        self.id = uuid4()
        self.risk_score = risk_score
        self.confidence = confidence
        self.category = category
        self.user_id = user_id
        self.context_id = context_id
        self.indicators = indicators or []


def test_threat_pipeline():
    user_id = uuid4()
    context_id = uuid4()

    detection = MockDetection(
        risk_score=85,
        confidence=0.95,
        category="phishing_url",
        user_id=user_id,
        context_id=context_id,
        indicators=["suspicious_domain"],
    )

    score_service = ScoreService()
    notification_service = NotificationService()

    pipeline = SecurityPipeline(
        score_service,
        notification_service,
    )

    result = pipeline.process(detection)

    assert result.risk_level == "CRITICAL"
    assert result.risk_score == 85
    assert result.cyber_score == 49
    assert result.incident_created is True
    assert result.incident_status == IncidentStatus.DETECTED
    assert result.notification_id is not None

    notification = notification_service.get(result.notification_id)

    assert notification is not None
    assert notification.detection_id == detection.id
    assert notification.context_id == context_id