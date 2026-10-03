from dataclasses import dataclass
from datetime import datetime, UTC
from uuid import UUID, uuid4

from app.incidents.contracts import IncidentStatus
from app.incidents.service import IncidentStateMachine
from app.notifications.contracts import (
    NotificationEvent,
    NotificationKind,
)
from app.notifications.service import NotificationService
from app.policy.contracts import PolicyContext
from app.policy.engine import evaluate_policy
from app.response.service import recommend_response
from app.risk.engine import evaluate_risk
from app.scoring.service import ScoreService

from app.orchestration.service import (
    AlertType,
    Severity,
    alert_orchestration_service,
    audit_service,
    incident_correlation_service,
    incident_timeline_service,
    severity_router,
    warning_escalation_service,
    TimelineStage,
)


@dataclass(frozen=True)
class PipelineResult:
    detection_id: UUID
    risk_level: str
    risk_score: float
    cyber_score: int
    incident_created: bool
    incident_status: IncidentStatus | None
    notification_id: str | None
    policy_decision: str
    alert_id: str | None
    correlation_key: str | None
    warning_level: str | None
    recommendations: tuple


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
        user_uuid = detection.user_id
        user_id = str(user_uuid)

        # ---------------------------------------------------------
        # 1. DETECTION -> RISK
        # ---------------------------------------------------------
        risk = evaluate_risk(detection)

        severity = severity_router.classify(
            int(risk.risk_score)
        )

        routing = severity_router.route(severity)

        # ---------------------------------------------------------
        # 2. RISK -> POLICY
        # ---------------------------------------------------------
        policy_context = PolicyContext(
            risk_score=risk.risk_score,
            confidence=risk.confidence,
            category=risk.category,
            user_context=user_id,
        )

        policy_result = evaluate_policy(policy_context)

        # ---------------------------------------------------------
        # 3. RISK -> CYBER SCORE
        # ---------------------------------------------------------
        threat_detected = severity in {
            Severity.HIGH,
            Severity.CRITICAL,
        }

        score_event = self.score_service.record_score_event(
            user_id,
            threat_detected=threat_detected,
            reason=f"{severity.value}: {risk.category}",
        )

        # ---------------------------------------------------------
        # 4. INCIDENT CORRELATION
        # ---------------------------------------------------------
        incident_created = False
        incident_status = None
        correlation_key = None
        correlated_incident = None

        should_create_incident = (
            routing.incident
            or policy_result.create_incident
        )

        event_id = getattr(
            detection,
            "event_id",
            UUID(int=0),
        )

        target = getattr(
            detection,
            "target",
            None,
        )

        if should_create_incident:
            correlation_key = (
                incident_correlation_service.build_key(
                    user_id=user_id,
                    category=risk.category,
                    target=target,
                )
            )

            correlated_incident, incident_created = (
                incident_correlation_service.correlate(
                    user_id=user_id,
                    category=risk.category,
                    target=target,
                    detection_id=detection_id,
                    event_id=event_id,
                    severity=severity,
                )
            )

            incident_status = IncidentStatus.DETECTED

            if incident_created:
                incident_timeline_service.add(
                    correlated_incident.id,
                    TimelineStage.DETECTION,
                    actor="system",
                    details=(
                        f"Detection {detection_id} received."
                    ),
                )

                incident_timeline_service.add(
                    correlated_incident.id,
                    TimelineStage.RISK_ASSESSMENT,
                    actor="system",
                    details=(
                        f"Risk {severity.value} "
                        f"({risk.risk_score})."
                    ),
                )

                # Validate the existing incident state machine.
                IncidentStateMachine.transition(
                    IncidentStatus.DETECTED,
                    IncidentStatus.ANALYZING,
                )

        # ---------------------------------------------------------
        # 5. ALERT + NOTIFICATION
        # ---------------------------------------------------------
        alert_id = None
        notification_id = None

        should_alert = (
            routing.alert
            or policy_result.create_alert
        )

        if should_alert:
            if severity == Severity.CRITICAL:
                alert_type = AlertType.CRITICAL_INCIDENT
            elif severity == Severity.HIGH:
                alert_type = AlertType.HIGH_RISK_DETECTION
            else:
                alert_type = AlertType.THREAT_DETECTED

            alert = alert_orchestration_service.create(
                alert_type=alert_type,
                severity=severity,
                message=(
                    f"{severity.value} risk detected: "
                    f"{risk.category}."
                ),
                user_id=user_id,
                incident_id=(
                    correlated_incident.id
                    if correlated_incident
                    else None
                ),
                detection_id=detection_id,
                urgent=routing.urgent,
            )

            alert_id = str(alert.id)

            timeline_id = (
                correlated_incident.id
                if correlated_incident
                else detection_id
            )

            incident_timeline_service.add(
                timeline_id,
                TimelineStage.ALERT,
                actor="system",
                details=f"Alert {alert.id} created.",
            )

            notification = NotificationEvent(
                recipient_id=user_uuid,
                context_id=getattr(
                    detection,
                    "context_id",
                    UUID(int=0),
                ),
                kind=(
                    NotificationKind.INCIDENT
                    if correlated_incident
                    else NotificationKind.THREAT
                ),
                title="Security threat detected",
                body=(
                    f"{severity.value} risk detected for "
                    f"{risk.category}."
                ),
                occurred_at=datetime.now(UTC),
                incident_id=(
                    correlated_incident.id
                    if correlated_incident
                    else None
                ),
                detection_id=detection_id,
            )

            notification_id = (
                self.notification_service.enqueue(
                    notification
                )
            )

        # ---------------------------------------------------------
        # 6. WARNING ESCALATION
        # ---------------------------------------------------------
        warning_level = None

        if severity in {
            Severity.HIGH,
            Severity.CRITICAL,
        }:
            warning_level = (
                warning_escalation_service.record_warning(
                    user_id
                )
            )

            if warning_level == "TEMPORARY_SUSPENSION":
                audit_service.record(
                    actor="system",
                    action="TEMPORARY_SUSPENSION",
                    target=user_id,
                    reason="Warning threshold reached.",
                    outcome="suspended",
                )

        # ---------------------------------------------------------
        # 7. RESPONSE RECOMMENDATIONS
        # ---------------------------------------------------------
        recommendations = tuple(
            recommend_response(
                risk_level=severity.value,
                category=risk.category,
            )
        )

        for recommendation in recommendations:
            audit_service.record(
                actor="system",
                action="RECOMMEND_RESPONSE",
                target=user_id,
                reason=recommendation.reason,
                outcome=recommendation.action.value,
            )

        # ---------------------------------------------------------
        # 8. PIPELINE AUDIT
        # ---------------------------------------------------------
        audit_service.record(
            actor="system",
            action="SECURITY_PIPELINE",
            target=user_id,
            reason=(
                f"{risk.category}: "
                f"{severity.value}"
            ),
            outcome=policy_result.decision.value,
        )

        return PipelineResult(
            detection_id=detection_id,
            risk_level=severity.value,
            risk_score=risk.risk_score,
            cyber_score=score_event.new_score,
            incident_created=incident_created,
            incident_status=incident_status,
            notification_id=notification_id,
            policy_decision=policy_result.decision.value,
            alert_id=alert_id,
            correlation_key=correlation_key,
            warning_level=warning_level,
            recommendations=recommendations,
        )
