from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from app.incidents.contracts import IncidentStatus
from app.incidents.service import IncidentStateMachine
from app.notifications.contracts import (
    NotificationEvent,
    NotificationKind,
)
from app.notifications.service import NotificationService
from app.risk.engine import evaluate_risk
from app.scoring.service import ScoreService


@dataclass(frozen=True)
class PipelineResult:
    detection_id: UUID
    risk_level: str
    risk_score: float
    cyber_score: int
    incident_created: bool
    incident_status: IncidentStatus | None
    notification_id: str | None


class SecurityPipeline:
    def __init__(
        self,
        score_service: ScoreService,
        notification_service: NotificationService,
    ):
        self.score_service = score_service
        self.notification_service = notification_service

    def process(self, detection) -> PipelineResult:
        detection_id = getattr(detection, "id", uuid4())
        user_id = str(detection.user_id)

        risk = evaluate_risk(detection)
        threat_detected = risk.level.value in {"HIGH", "CRITICAL"}

        score_event = self.score_service.record_score_event(
            user_id,
            threat_detected=threat_detected,
            reason=f"{risk.level.value}: {detection.category}",
        )

        incident_created = False
        incident_status = None
        notification_id = None

        if threat_detected:
            incident_created = True
            incident_status = IncidentStatus.DETECTED

            # Validate the first lifecycle transition.
            IncidentStateMachine.transition(
                IncidentStatus.DETECTED,
                IncidentStatus.ANALYZING,
            )

            context_id = getattr(detection, "context_id", UUID(int=0))

            notification = NotificationEvent(
                recipient_id=UUID(str(detection.user_id)),
                context_id=context_id,
                kind=NotificationKind.THREAT,
                title="Security threat detected",
                body=(
                    f"{risk.level.value} risk detected for "
                    f"{detection.category}."
                ),
                occurred_at=datetime.utcnow(),
                detection_id=detection_id,
            )

            notification_id = self.notification_service.enqueue(notification)

        return PipelineResult(
            detection_id=detection_id,
            risk_level=risk.level.value,
            risk_score=risk.risk_score,
            cyber_score=self.score_service.get_current_score(user_id).score,
            incident_created=incident_created,
            incident_status=incident_status,
            notification_id=notification_id,
        )