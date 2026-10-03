from datetime import datetime, UTC, timedelta
from uuid import uuid4

import pytest

from app.security.suspensions import (
    SuspensionService,
    SuspensionStatus,
)
from app.security.warnings import (
    SecurityWarningService,
    WarningLevel,
    WarningPolicy,
)


def test_warning_sequence_and_suspension():
    current_time = [datetime(2026, 1, 1, tzinfo=UTC)]

    def clock():
        return current_time[0]

    suspension_service = SuspensionService()

    service = SecurityWarningService(
        policy=WarningPolicy(
            low_score_threshold=40,
            warning_interval=timedelta(hours=1),
            suspension_duration=timedelta(hours=2),
        ),
        suspension_service=suspension_service,
        clock=clock,
    )

    subject_id = uuid4()
    organization_id = uuid4()

    result = service.evaluate(
        subject_id=subject_id,
        organization_id=organization_id,
        cyber_score=30,
    )

    assert result.warning_level == WarningLevel.WARNING_1
    assert result.warning_count == 1
    assert result.suspended is False

    current_time[0] += timedelta(hours=1)

    result = service.evaluate(
        subject_id=subject_id,
        organization_id=organization_id,
        cyber_score=30,
    )

    assert result.warning_level == WarningLevel.WARNING_2
    assert result.warning_count == 2

    current_time[0] += timedelta(hours=1)

    result = service.evaluate(
        subject_id=subject_id,
        organization_id=organization_id,
        cyber_score=30,
    )

    assert result.warning_level == WarningLevel.WARNING_3
    assert result.warning_count == 3
    assert result.suspended is False

    current_time[0] += timedelta(hours=1)

    result = service.evaluate(
        subject_id=subject_id,
        organization_id=organization_id,
        cyber_score=30,
    )

    assert result.warning_level == WarningLevel.SUSPENSION
    assert result.suspended is True
    assert result.suspension is not None
    assert result.suspension.status == SuspensionStatus.ACTIVE


def test_warning_does_not_repeat_before_interval():
    current_time = [datetime(2026, 1, 1, tzinfo=UTC)]

    service = SecurityWarningService(
        policy=WarningPolicy(
            low_score_threshold=40,
            warning_interval=timedelta(hours=1),
        ),
        suspension_service=SuspensionService(),
        clock=lambda: current_time[0],
    )

    subject_id = uuid4()
    organization_id = uuid4()

    first = service.evaluate(
        subject_id=subject_id,
        organization_id=organization_id,
        cyber_score=20,
    )

    second = service.evaluate(
        subject_id=subject_id,
        organization_id=organization_id,
        cyber_score=20,
    )

    assert first.warning_level == WarningLevel.WARNING_1
    assert second.warning_level is None
    assert second.warning_count == 1


def test_score_recovery_resets_warning_sequence():
    current_time = [datetime(2026, 1, 1, tzinfo=UTC)]

    service = SecurityWarningService(
        policy=WarningPolicy(
            low_score_threshold=40,
            warning_interval=timedelta(hours=1),
        ),
        suspension_service=SuspensionService(),
        clock=lambda: current_time[0],
    )

    subject_id = uuid4()
    organization_id = uuid4()

    first = service.evaluate(
        subject_id=subject_id,
        organization_id=organization_id,
        cyber_score=30,
    )

    assert first.warning_count == 1

    current_time[0] += timedelta(minutes=30)

    recovered = service.evaluate(
        subject_id=subject_id,
        organization_id=organization_id,
        cyber_score=50,
    )

    assert recovered.warning_level is None
    assert recovered.warning_count == 0

    next_warning = service.evaluate(
        subject_id=subject_id,
        organization_id=organization_id,
        cyber_score=30,
    )

    assert next_warning.warning_level == WarningLevel.WARNING_1
    assert next_warning.warning_count == 1


def test_suspension_expires():
    current_time = [datetime(2026, 1, 1, tzinfo=UTC)]

    suspension_service = SuspensionService()

    subject_id = uuid4()
    organization_id = uuid4()

    suspension = suspension_service.create(
        subject_id=subject_id,
        organization_id=organization_id,
        reason="Test suspension",
        trigger="WARNING_3",
        duration=timedelta(hours=1),
        now=current_time[0],
    )

    assert suspension.status == SuspensionStatus.ACTIVE

    assert suspension_service.is_active(
        subject_id,
        now=current_time[0],
    ) is True

    current_time[0] += timedelta(hours=2)

    refreshed = suspension_service.refresh_status(
        suspension.id,
        now=current_time[0],
    )

    assert refreshed.status == SuspensionStatus.EXPIRED

    assert suspension_service.is_active(
        subject_id,
        now=current_time[0],
    ) is False


def test_suspension_contains_audit_information():
    service = SuspensionService()

    subject_id = uuid4()
    organization_id = uuid4()

    suspension = service.create(
        subject_id=subject_id,
        organization_id=organization_id,
        reason="Low Cyber Score",
        trigger="WARNING_3",
        duration=timedelta(hours=24),
        created_by="system",
        audit_info="Automatic security workflow",
    )

    assert suspension.subject_id == subject_id
    assert suspension.organization_id == organization_id
    assert suspension.reason == "Low Cyber Score"
    assert suspension.trigger == "WARNING_3"
    assert suspension.created_by == "system"
    assert suspension.audit_info == "Automatic security workflow"
    assert suspension.expires_at > suspension.started_at


def test_invalid_score_is_rejected():
    service = SecurityWarningService(
        policy=WarningPolicy(low_score_threshold=40),
        suspension_service=SuspensionService(),
    )

    with pytest.raises(ValueError):
        service.evaluate(
            subject_id=uuid4(),
            organization_id=uuid4(),
            cyber_score=101,
        )

    with pytest.raises(ValueError):
        service.evaluate(
            subject_id=uuid4(),
            organization_id=uuid4(),
            cyber_score=-1,
        )