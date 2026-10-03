import pytest

from app.incidents.service import create_incident, transition_incident
from app.incidents.states import IncidentState


def test_incident_starts_as_detected():
    incident = create_incident("I001", "U001", "ATO", 85, 0.92)

    assert incident.state == IncidentState.DETECTED


def test_valid_transition():
    incident = create_incident("I001", "U001", "ATO", 85, 0.92)

    transition_incident(incident, IncidentState.ANALYZING)

    assert incident.state == IncidentState.ANALYZING


def test_invalid_transition():
    incident = create_incident("I001", "U001", "ATO", 85, 0.92)

    with pytest.raises(ValueError):
        transition_incident(incident, IncidentState.CLOSED)