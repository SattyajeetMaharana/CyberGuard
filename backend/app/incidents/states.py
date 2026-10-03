from enum import Enum


class IncidentState(str, Enum):
    DETECTED = "DETECTED"
    ANALYZING = "ANALYZING"
    CONFIRMED = "CONFIRMED"
    CONTAINMENT = "CONTAINMENT"
    RESOLUTION = "RESOLUTION"
    CLOSED = "CLOSED"