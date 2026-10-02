from .contracts import IncidentStatus


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
                f"Cannot transition incident from {current} to {target}"
            )
        return target