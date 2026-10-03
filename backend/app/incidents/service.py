from datetime import datetime, UTC
from uuid import UUID, uuid4

from .contracts import (
    Incident,
    IncidentCreate,
    IncidentStatus,
)


class InvalidIncidentTransition(ValueError):
    """Raised when an incident skips or reverses a lifecycle state."""


class IncidentStateMachine:
    _next = {
        IncidentStatus.DETECTED: IncidentStatus.ANALYZING,
        IncidentStatus.ANALYZING: IncidentStatus.CONFIRMED,
        IncidentStatus.CONFIRMED: IncidentStatus.CONTAINMENT,
        IncidentStatus.CONTAINMENT: IncidentStatus.RESOLUTION,
        IncidentStatus.RESOLUTION: IncidentStatus.CLOSED,
        IncidentStatus.CLOSED: None,
    }

    @classmethod
    def transition(
        cls,
        current: IncidentStatus,
        target: IncidentStatus,
    ) -> IncidentStatus:
        if cls._next[current] != target:
            raise InvalidIncidentTransition(
                f"Cannot transition incident from "
                f"{current} to {target}"
            )

        return target


class IncidentService:
    def __init__(self):
        self._incidents: dict[UUID, Incident] = {}

    def create(
        self,
        data: IncidentCreate,
    ) -> Incident:
        now = datetime.now(UTC)

        incident = Incident(
            id=uuid4(),
            context_id=data.context_id,
            severity=data.severity,
            status=IncidentStatus.DETECTED,
            detected_at=data.detected_at,
            created_at=now,
            updated_at=now,
            primary_detection_id=data.primary_detection_id,
        )

        self._incidents[incident.id] = incident

        return incident

    def get(
        self,
        incident_id: UUID,
    ) -> Incident | None:
        return self._incidents.get(incident_id)

    def transition(
        self,
        incident_id: UUID,
        target: IncidentStatus,
    ) -> Incident:
        incident = self._incidents.get(incident_id)

        if incident is None:
            raise KeyError(
                f"Incident {incident_id} not found"
            )

        IncidentStateMachine.transition(
            incident.status,
            target,
        )

        now = datetime.now(UTC)

        incident.status = target
        incident.updated_at = now

        if target == IncidentStatus.RESOLUTION:
            incident.resolved_at = now

        if target == IncidentStatus.CLOSED:
            incident.closed_at = now

        return incident


incident_service = IncidentService()
# Backward-compatible API for the original incident tests.

from .states import IncidentState


def create_incident(
    incident_id: str,
    user_id: str,
    category: str,
    risk_score: int,
    confidence: float,
):
    class LegacyIncident:
        def __init__(self):
            self.id = incident_id
            self.user_id = user_id
            self.category = category
            self.risk_score = risk_score
            self.confidence = confidence
            self.state = IncidentState.DETECTED

    return LegacyIncident()


def transition_incident(
    incident,
    target: IncidentState,
):
    valid_transitions = {
        IncidentState.DETECTED: IncidentState.ANALYZING,
        IncidentState.ANALYZING: IncidentState.CONFIRMED,
        IncidentState.CONFIRMED: IncidentState.CONTAINMENT,
        IncidentState.CONTAINMENT: IncidentState.RESOLUTION,
        IncidentState.RESOLUTION: IncidentState.CLOSED,
    }

    if valid_transitions.get(incident.state) != target:
        raise ValueError(
            f"Cannot transition incident from "
            f"{incident.state} to {target}"
        )

    incident.state = target
    return incident
