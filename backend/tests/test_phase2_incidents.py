from datetime import datetime, UTC
from uuid import uuid4

import pytest

from app.incidents.contracts import (
    IncidentCreate,
    IncidentStatus,
)
from app.incidents.service import (
    IncidentService,
    InvalidIncidentTransition,
)


def test_incident_starts_detected():
    service = IncidentService()

    incident = service.create(
        IncidentCreate(
            context_id=uuid4(),
            severity="HIGH",
            detected_at=datetime.now(UTC),
        )
    )

    assert incident.status == IncidentStatus.DETECTED
    assert incident.created_at is not None
    assert incident.updated_at is not None


def test_incident_follows_valid_lifecycle():
    service = IncidentService()

    incident = service.create(
        IncidentCreate(
            context_id=uuid4(),
            severity="HIGH",
            detected_at=datetime.now(UTC),
        )
    )

    service.transition(
        incident.id,
        IncidentStatus.ANALYZING,
    )

    service.transition(
        incident.id,
        IncidentStatus.CONFIRMED,
    )

    service.transition(
        incident.id,
        IncidentStatus.CONTAINMENT,
    )

    service.transition(
        incident.id,
        IncidentStatus.RESOLUTION,
    )

    service.transition(
        incident.id,
        IncidentStatus.CLOSED,
    )

    assert incident.status == IncidentStatus.CLOSED
    assert incident.resolved_at is not None
    assert incident.closed_at is not None


def test_incident_cannot_skip_state():
    service = IncidentService()

    incident = service.create(
        IncidentCreate(
            context_id=uuid4(),
            severity="HIGH",
            detected_at=datetime.now(UTC),
        )
    )

    with pytest.raises(InvalidIncidentTransition):
        service.transition(
            incident.id,
            IncidentStatus.CONFIRMED,
        )