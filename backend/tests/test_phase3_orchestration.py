from uuid import uuid4

import pytest

from app.orchestration.service import (
    AlertOrchestrationService,
    AlertType,
    AuditService,
    IncidentCorrelationService,
    IncidentTimelineService,
    ResponseAction,
    ResponseApprovalService,
    ResponseState,
    Severity,
    SeverityRouter,
    TimelineStage,
    WarningEscalationService,
)


def test_severity_boundaries():
    router = SeverityRouter()

    assert router.classify(0) == Severity.SAFE
    assert router.classify(19) == Severity.SAFE

    assert router.classify(20) == Severity.LOW
    assert router.classify(39) == Severity.LOW

    assert router.classify(40) == Severity.MEDIUM
    assert router.classify(59) == Severity.MEDIUM

    assert router.classify(60) == Severity.HIGH
    assert router.classify(79) == Severity.HIGH

    assert router.classify(80) == Severity.CRITICAL
    assert router.classify(100) == Severity.CRITICAL


def test_invalid_risk_score():
    router = SeverityRouter()

    with pytest.raises(ValueError):
        router.classify(-1)

    with pytest.raises(ValueError):
        router.classify(101)


def test_severity_routing():
    router = SeverityRouter()

    safe = router.route(Severity.SAFE)
    assert safe.record is True
    assert safe.alert is False
    assert safe.incident is False

    medium = router.route(Severity.MEDIUM)
    assert medium.alert is True
    assert medium.incident is False

    high = router.route(Severity.HIGH)
    assert high.alert is True
    assert high.incident is True
    assert high.policy_review is False

    critical = router.route(Severity.CRITICAL)
    assert critical.alert is True
    assert critical.incident is True
    assert critical.policy_review is True
    assert critical.urgent is True


def test_incident_correlation_creates_one_incident():
    service = IncidentCorrelationService()

    incident1, created1 = service.correlate(
        user_id="user-1",
        category="account_takeover",
        target="account-1",
        detection_id=uuid4(),
        event_id=uuid4(),
        severity=Severity.HIGH,
    )

    incident2, created2 = service.correlate(
        user_id="user-1",
        category="account_takeover",
        target="account-1",
        detection_id=uuid4(),
        event_id=uuid4(),
        severity=Severity.HIGH,
    )

    assert created1 is True
    assert created2 is False
    assert incident1.id == incident2.id
    assert len(incident2.detection_ids) == 2
    assert len(incident2.event_ids) == 2


def test_duplicate_detection_does_not_create_duplicate():
    service = IncidentCorrelationService()

    detection_id = uuid4()

    incident1, created1 = service.correlate(
        user_id="user-1",
        category="phishing_url",
        target="example.com",
        detection_id=detection_id,
        event_id=uuid4(),
        severity=Severity.HIGH,
    )

    incident2, created2 = service.correlate(
        user_id="user-1",
        category="phishing_url",
        target="example.com",
        detection_id=detection_id,
        event_id=uuid4(),
        severity=Severity.CRITICAL,
    )

    assert created1 is True
    assert created2 is False
    assert incident1.id == incident2.id
    assert len(incident2.detection_ids) == 1


def test_severity_of_correlated_incident_can_escalate():
    service = IncidentCorrelationService()

    incident, _ = service.correlate(
        user_id="user-1",
        category="account_takeover",
        target="account-1",
        detection_id=uuid4(),
        event_id=uuid4(),
        severity=Severity.MEDIUM,
    )

    service.correlate(
        user_id="user-1",
        category="account_takeover",
        target="account-1",
        detection_id=uuid4(),
        event_id=uuid4(),
        severity=Severity.CRITICAL,
    )

    assert incident.severity == Severity.CRITICAL


def test_alert_creation_and_acknowledgement():
    service = AlertOrchestrationService()

    alert = service.create(
        alert_type=AlertType.HIGH_RISK_DETECTION,
        severity=Severity.HIGH,
        message="High-risk security event detected.",
        user_id="user-1",
    )

    assert alert.acknowledged is False
    assert alert.urgent is False

    service.acknowledge(alert.id)

    assert alert.acknowledged is True


def test_critical_alert_is_urgent():
    service = AlertOrchestrationService()

    alert = service.create(
        alert_type=AlertType.CRITICAL_INCIDENT,
        severity=Severity.CRITICAL,
        message="Critical incident detected.",
        urgent=True,
    )

    assert alert.urgent is True
    assert alert.severity == Severity.CRITICAL


def test_response_cannot_skip_admin_review():
    service = ResponseApprovalService()

    response = ResponseAction(
        id=uuid4(),
        category="malicious_url",
        actions=["Do not open the URL."],
    )

    with pytest.raises(ValueError):
        service.execute(response)

    assert response.state == ResponseState.RECOMMENDED


def test_response_approval_sequence():
    service = ResponseApprovalService()

    response = ResponseAction(
        id=uuid4(),
        category="phishing",
        actions=["Verify the sender."],
    )

    service.submit_for_review(response)
    assert response.state == ResponseState.ADMIN_REVIEW

    service.approve(response)
    assert response.state == ResponseState.APPROVED

    service.execute(response)
    assert response.state == ResponseState.EXECUTED


def test_warning_escalation():
    service = WarningEscalationService(
        suspension_threshold=3
    )

    assert service.record_warning("user-1") == "WARNING_1"
    assert service.record_warning("user-1") == "WARNING_2"
    assert service.record_warning("user-1") == "TEMPORARY_SUSPENSION"

    assert service.warning_count("user-1") == 3
    assert service.is_suspended("user-1") is True


def test_incident_timeline():
    service = IncidentTimelineService()
    incident_id = uuid4()

    service.add(
        incident_id,
        TimelineStage.DETECTION,
        details="Detection received",
    )

    service.add(
        incident_id,
        TimelineStage.RISK_ASSESSMENT,
        details="Risk calculated",
    )

    service.add(
        incident_id,
        TimelineStage.ALERT,
        details="Alert generated",
    )

    timeline = service.get(incident_id)

    assert len(timeline) == 3
    assert timeline[0].stage == TimelineStage.DETECTION
    assert timeline[1].stage == TimelineStage.RISK_ASSESSMENT
    assert timeline[2].stage == TimelineStage.ALERT


def test_audit_event():
    service = AuditService()

    event = service.record(
        actor="admin-1",
        action="APPROVE_RESPONSE",
        target="incident-1",
        reason="Security review completed",
        outcome="approved",
    )

    assert event.actor == "admin-1"
    assert event.action == "APPROVE_RESPONSE"
    assert event.target == "incident-1"
    assert event.reason == "Security review completed"
    assert event.outcome == "approved"
