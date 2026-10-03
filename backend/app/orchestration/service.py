from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import StrEnum
from uuid import UUID, uuid4


class Severity(StrEnum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(StrEnum):
    THREAT_DETECTED = "THREAT_DETECTED"
    HIGH_RISK_DETECTION = "HIGH_RISK_DETECTION"
    CRITICAL_INCIDENT = "CRITICAL_INCIDENT"
    CYBER_SCORE_WARNING = "CYBER_SCORE_WARNING"
    DEVICE_ANOMALY = "DEVICE_ANOMALY"
    ACCOUNT_SECURITY_EVENT = "ACCOUNT_SECURITY_EVENT"
    SUSPENSION = "SUSPENSION"


class ResponseState(StrEnum):
    RECOMMENDED = "RECOMMENDED"
    ADMIN_REVIEW = "ADMIN_REVIEW"
    APPROVED = "APPROVED"
    EXECUTED = "EXECUTED"


class TimelineStage(StrEnum):
    DETECTION = "DETECTION"
    RISK_ASSESSMENT = "RISK_ASSESSMENT"
    ALERT = "ALERT"
    ACKNOWLEDGEMENT = "ACKNOWLEDGEMENT"
    CONTAINMENT = "CONTAINMENT"
    RESOLUTION = "RESOLUTION"
    CLOSED = "CLOSED"


@dataclass
class SeverityRouting:
    record: bool
    alert: bool
    incident: bool
    policy_review: bool
    urgent: bool


class SeverityRouter:
    """
    Phase 3 severity routing.

    Default rules:
        SAFE     -> record
        LOW      -> record
        MEDIUM   -> alert
        HIGH     -> incident + alert
        CRITICAL -> incident + urgent alert + policy review
    """

    def __init__(
        self,
        *,
        low_threshold: int = 20,
        medium_threshold: int = 40,
        high_threshold: int = 60,
        critical_threshold: int = 80,
    ):
        self.low_threshold = low_threshold
        self.medium_threshold = medium_threshold
        self.high_threshold = high_threshold
        self.critical_threshold = critical_threshold

    def classify(self, risk_score: int) -> Severity:
        if not 0 <= risk_score <= 100:
            raise ValueError("risk_score must be between 0 and 100")

        if risk_score >= self.critical_threshold:
            return Severity.CRITICAL

        if risk_score >= self.high_threshold:
            return Severity.HIGH

        if risk_score >= self.medium_threshold:
            return Severity.MEDIUM

        if risk_score >= self.low_threshold:
            return Severity.LOW

        return Severity.SAFE

    def route(self, severity: Severity) -> SeverityRouting:
        return SeverityRouting(
            record=True,
            alert=severity in {
                Severity.MEDIUM,
                Severity.HIGH,
                Severity.CRITICAL,
            },
            incident=severity in {
                Severity.HIGH,
                Severity.CRITICAL,
            },
            policy_review=severity == Severity.CRITICAL,
            urgent=severity == Severity.CRITICAL,
        )


@dataclass
class CorrelatedIncident:
    id: UUID
    correlation_key: str
    detection_ids: list[UUID] = field(default_factory=list)
    event_ids: list[UUID] = field(default_factory=list)
    severity: Severity = Severity.LOW
    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )


class IncidentCorrelationService:
    """
    Groups related detections/events into one logical incident.

    A detection is indexed so the same detection cannot create
    a duplicate incident.
    """

    def __init__(self):
        self._incidents: dict[str, CorrelatedIncident] = {}
        self._detection_index: dict[UUID, UUID] = {}

    @staticmethod
    def _severity_value(severity: Severity) -> int:
        return {
            Severity.SAFE: 0,
            Severity.LOW: 1,
            Severity.MEDIUM: 2,
            Severity.HIGH: 3,
            Severity.CRITICAL: 4,
        }[severity]

    def build_key(
        self,
        *,
        user_id: str | None,
        category: str,
        target: str | None = None,
    ) -> str:
        return "|".join(
            [
                user_id or "unknown",
                category.strip().lower(),
                target or "unknown",
            ]
        )

    def correlate(
        self,
        *,
        user_id: str | None,
        category: str,
        target: str | None,
        detection_id: UUID,
        event_id: UUID,
        severity: Severity,
    ) -> tuple[CorrelatedIncident, bool]:
        # Same detection must never create another incident.
        existing_incident_id = self._detection_index.get(detection_id)

        if existing_incident_id is not None:
            for incident in self._incidents.values():
                if incident.id == existing_incident_id:
                    return incident, False

        key = self.build_key(
            user_id=user_id,
            category=category,
            target=target,
        )

        now = datetime.now(UTC)
        incident = self._incidents.get(key)

        # Related event: add it to the existing incident.
        if incident is not None:
            if detection_id not in incident.detection_ids:
                incident.detection_ids.append(detection_id)

            if event_id not in incident.event_ids:
                incident.event_ids.append(event_id)

            if self._severity_value(severity) > self._severity_value(
                incident.severity
            ):
                incident.severity = severity

            incident.updated_at = now
            self._detection_index[detection_id] = incident.id

            return incident, False

        # No related incident exists.
        incident = CorrelatedIncident(
            id=uuid4(),
            correlation_key=key,
            detection_ids=[detection_id],
            event_ids=[event_id],
            severity=severity,
            created_at=now,
            updated_at=now,
        )

        self._incidents[key] = incident
        self._detection_index[detection_id] = incident.id

        return incident, True

    def get(self, correlation_key: str) -> CorrelatedIncident | None:
        return self._incidents.get(correlation_key)


@dataclass
class AlertRecord:
    id: UUID
    alert_type: AlertType
    severity: Severity
    message: str
    user_id: str | None
    incident_id: UUID | None
    detection_id: UUID | None
    urgent: bool
    acknowledged: bool
    created_at: datetime


class AlertOrchestrationService:
    """
    Creates structured alert records.

    Actual delivery can later be delegated to the existing
    notification service/provider system.
    """

    def __init__(self):
        self._alerts: list[AlertRecord] = []

    def create(
        self,
        *,
        alert_type: AlertType,
        severity: Severity,
        message: str,
        user_id: str | None = None,
        incident_id: UUID | None = None,
        detection_id: UUID | None = None,
        urgent: bool = False,
    ) -> AlertRecord:
        alert = AlertRecord(
            id=uuid4(),
            alert_type=alert_type,
            severity=severity,
            message=message,
            user_id=user_id,
            incident_id=incident_id,
            detection_id=detection_id,
            urgent=urgent,
            acknowledged=False,
            created_at=datetime.now(UTC),
        )

        self._alerts.append(alert)
        return alert

    def acknowledge(self, alert_id: UUID) -> AlertRecord:
        for alert in self._alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return alert

        raise KeyError(f"Alert {alert_id} not found")

    def list_alerts(self) -> list[AlertRecord]:
        return list(self._alerts)


@dataclass
class TimelineEntry:
    stage: TimelineStage
    timestamp: datetime
    actor: str | None = None
    details: str | None = None


class IncidentTimelineService:
    def __init__(self):
        self._timelines: dict[UUID, list[TimelineEntry]] = {}

    def add(
        self,
        incident_id: UUID,
        stage: TimelineStage,
        *,
        actor: str | None = None,
        details: str | None = None,
    ) -> TimelineEntry:
        entry = TimelineEntry(
            stage=stage,
            timestamp=datetime.now(UTC),
            actor=actor,
            details=details,
        )

        self._timelines.setdefault(
            incident_id,
            [],
        ).append(entry)

        return entry

    def get(self, incident_id: UUID) -> list[TimelineEntry]:
        return list(self._timelines.get(incident_id, []))


@dataclass
class ResponseAction:
    id: UUID
    category: str
    actions: list[str]
    state: ResponseState = ResponseState.RECOMMENDED
    target: str | None = None
    reason: str | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )


class ResponseApprovalService:
    """
    Enforces:

        RECOMMENDED
             ↓
        ADMIN_REVIEW
             ↓
          APPROVED
             ↓
          EXECUTED

    A response cannot skip approval.
    """

    _next = {
        ResponseState.RECOMMENDED: ResponseState.ADMIN_REVIEW,
        ResponseState.ADMIN_REVIEW: ResponseState.APPROVED,
        ResponseState.APPROVED: ResponseState.EXECUTED,
        ResponseState.EXECUTED: None,
    }

    def submit_for_review(
        self,
        response: ResponseAction,
    ) -> ResponseAction:
        self._transition(
            response,
            ResponseState.ADMIN_REVIEW,
        )
        return response

    def approve(
        self,
        response: ResponseAction,
    ) -> ResponseAction:
        self._transition(
            response,
            ResponseState.APPROVED,
        )
        return response

    def execute(
        self,
        response: ResponseAction,
    ) -> ResponseAction:
        self._transition(
            response,
            ResponseState.EXECUTED,
        )
        return response

    def _transition(
        self,
        response: ResponseAction,
        target: ResponseState,
    ) -> None:
        if self._next[response.state] != target:
            raise ValueError(
                f"Cannot transition response from "
                f"{response.state} to {target}"
            )

        response.state = target


class WarningEscalationService:
    """
    Warning sequence:

        Warning 1
           ↓
        Warning 2
           ↓
        Warning 3
           ↓
        Temporary Suspension
    """

    def __init__(self, *, suspension_threshold: int = 3):
        if suspension_threshold < 1:
            raise ValueError(
                "suspension_threshold must be at least 1"
            )

        self.suspension_threshold = suspension_threshold
        self._counts: dict[str, int] = {}
        self._suspended: set[str] = set()

    def record_warning(self, user_id: str) -> str:
        if user_id in self._suspended:
            return "TEMPORARY_SUSPENSION"

        count = self._counts.get(user_id, 0) + 1
        self._counts[user_id] = count

        if count >= self.suspension_threshold:
            self._suspended.add(user_id)
            return "TEMPORARY_SUSPENSION"

        return f"WARNING_{count}"

    def warning_count(self, user_id: str) -> int:
        return self._counts.get(user_id, 0)

    def is_suspended(self, user_id: str) -> bool:
        return user_id in self._suspended


@dataclass
class AuditEvent:
    id: UUID
    actor: str
    action: str
    target: str
    reason: str
    timestamp: datetime
    outcome: str


class AuditService:
    def __init__(self):
        self._events: list[AuditEvent] = []

    def record(
        self,
        *,
        actor: str,
        action: str,
        target: str,
        reason: str,
        outcome: str,
    ) -> AuditEvent:
        event = AuditEvent(
            id=uuid4(),
            actor=actor,
            action=action,
            target=target,
            reason=reason,
            timestamp=datetime.now(UTC),
            outcome=outcome,
        )

        self._events.append(event)
        return event

    def list_events(self) -> list[AuditEvent]:
        return list(self._events)


# Application-level services.
severity_router = SeverityRouter()
incident_correlation_service = IncidentCorrelationService()
alert_orchestration_service = AlertOrchestrationService()
incident_timeline_service = IncidentTimelineService()
response_approval_service = ResponseApprovalService()
warning_escalation_service = WarningEscalationService()
audit_service = AuditService()
