from datetime import timedelta
from uuid import uuid4

import pytest

from app.admin_security.workflow import (
    AdminSecurityWorkflow,
    ReportStatus,
    VoteChoice,
)
from app.notifications.contracts import (
    NotificationEvent,
    NotificationKind,
)
from app.policy.contracts import (
    PolicyContext,
    PolicyDecision,
    SecurityPolicy,
)
from app.policy.engine import evaluate_policy
from app.response.contracts import ResponseAction
from app.response.service import recommend_response
from app.security.suspensions import (
    SuspensionService,
    SuspensionStatus,
)


def test_high_risk_policy_creates_incident_and_alert():
    result = evaluate_policy(
        PolicyContext(
            risk_score=80,
            confidence=0.9,
            category="phishing_url",
        ),
        SecurityPolicy(
            minimum_risk_score=60,
            minimum_confidence=0.8,
        ),
    )

    assert result.decision == PolicyDecision.REQUIRE_ADMIN_REVIEW
    assert result.create_incident is True
    assert result.create_alert is True


def test_policy_below_threshold_allows_event():
    result = evaluate_policy(
        PolicyContext(
            risk_score=40,
            confidence=0.9,
            category="phishing_url",
        ),
        SecurityPolicy(
            minimum_risk_score=60,
            minimum_confidence=0.8,
        ),
    )

    assert result.decision == PolicyDecision.ALLOW
    assert result.create_incident is False
    assert result.create_alert is False


def test_policy_requires_configured_confidence():
    result = evaluate_policy(
        PolicyContext(
            risk_score=80,
            confidence=0.5,
            category="phishing_url",
        ),
        SecurityPolicy(
            minimum_risk_score=60,
            minimum_confidence=0.8,
        ),
    )

    assert result.decision == PolicyDecision.ALLOW


def test_response_recommendations_are_structured():
    recommendations = recommend_response(
        risk_level="HIGH",
        category="phishing_url",
    )

    actions = {recommendation.action for recommendation in recommendations}

    assert ResponseAction.DO_NOT_OPEN_URL in actions
    assert ResponseAction.VERIFY_DOMAIN in actions
    assert ResponseAction.REPORT_MESSAGE in actions
    assert ResponseAction.REMOVE_SUSPICIOUS_CONTENT in actions
    assert ResponseAction.NOTIFY_ADMIN in actions


def test_notification_event_supports_required_security_kinds():
    event = NotificationEvent(
        recipient_id=uuid4(),
        context_id=uuid4(),
        kind=NotificationKind.WARNING,
        title="Security warning",
        body="Cyber Score is below the configured threshold.",
        occurred_at=__import__("datetime").datetime.now(
            __import__("datetime").UTC
        ),
    )

    assert event.kind == NotificationKind.WARNING


def test_admin_target_cannot_vote():
    workflow = AdminSecurityWorkflow(SuspensionService())

    organization_id = uuid4()
    reporter_id = uuid4()
    target_id = uuid4()

    review = workflow.create_report(
        organization_id=organization_id,
        reporter_id=reporter_id,
        target_id=target_id,
        reason="Repeated security violations",
    )

    with pytest.raises(ValueError):
        workflow.cast_vote(
            review.report.id,
            admin_id=target_id,
            choice=VoteChoice.APPROVE,
        )


def test_admin_majority_approval_creates_suspension():
    suspension_service = SuspensionService()
    workflow = AdminSecurityWorkflow(suspension_service)

    organization_id = uuid4()
    reporter_id = uuid4()
    target_id = uuid4()
    admin_two = uuid4()
    admin_three = uuid4()

    review = workflow.create_report(
        organization_id=organization_id,
        reporter_id=reporter_id,
        target_id=target_id,
        reason="Repeated suspicious activity",
    )

    workflow.cast_vote(
        review.report.id,
        admin_id=reporter_id,
        choice=VoteChoice.APPROVE,
    )

    workflow.cast_vote(
        review.report.id,
        admin_id=admin_two,
        choice=VoteChoice.APPROVE,
    )

    workflow.cast_vote(
        review.report.id,
        admin_id=admin_three,
        choice=VoteChoice.REJECT,
    )

    status = workflow.decide(
        review.report.id,
        eligible_admin_ids={
            reporter_id,
            admin_two,
            admin_three,
            target_id,
        },
    )

    assert status == ReportStatus.APPROVED

    suspension = workflow.apply_decision(
        review.report.id,
        duration=timedelta(hours=24),
    )

    assert suspension is not None
    assert suspension.status == SuspensionStatus.ACTIVE
    assert suspension.subject_id == target_id


def test_admin_rejection_does_not_suspend():
    workflow = AdminSecurityWorkflow(SuspensionService())

    organization_id = uuid4()
    reporter_id = uuid4()
    target_id = uuid4()
    admin_two = uuid4()

    review = workflow.create_report(
        organization_id=organization_id,
        reporter_id=reporter_id,
        target_id=target_id,
        reason="Insufficient evidence",
    )

    workflow.cast_vote(
        review.report.id,
        admin_id=reporter_id,
        choice=VoteChoice.REJECT,
    )

    workflow.cast_vote(
        review.report.id,
        admin_id=admin_two,
        choice=VoteChoice.REJECT,
    )

    status = workflow.decide(
        review.report.id,
        eligible_admin_ids={
            reporter_id,
            admin_two,
            target_id,
        },
    )

    assert status == ReportStatus.REJECTED

    assert workflow.apply_decision(
        review.report.id,
        duration=timedelta(hours=24),
    ) is None