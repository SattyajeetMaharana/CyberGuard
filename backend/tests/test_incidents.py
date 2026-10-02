import pytest

from app.incidents.contracts import IncidentStatus
from app.incidents.service import (
    IncidentStateMachine,
    InvalidIncidentTransition,
)


def test_valid_incident_transition():
    result = IncidentStateMachine.transition(
        IncidentStatus.DETECTED,
        IncidentStatus.ANALYZING,
    )

    assert result == IncidentStatus.ANALYZING


def test_invalid_incident_transition():
    with pytest.raises(InvalidIncidentTransition):
        IncidentStateMachine.transition(
            IncidentStatus.DETECTED,
            IncidentStatus.CLOSED,
        )