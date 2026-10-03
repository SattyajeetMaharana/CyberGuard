from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID


class IncidentStatus(StrEnum):
    DETECTED = "DETECTED"
    ANALYZING = "ANALYZING"
    CONFIRMED = "CONFIRMED"
    CONTAINMENT = "CONTAINMENT"
    RESOLUTION = "RESOLUTION"
    CLOSED = "CLOSED"


@dataclass(frozen=True)
class IncidentCreate:
    context_id: UUID
    severity: str
    detected_at: datetime
    primary_detection_id: Optional[UUID] = None


@dataclass(frozen=True)
class IncidentUpdate:
    assigned_to: Optional[UUID] = None
    analyst_note: Optional[str] = None


@dataclass
class Incident:
    id: UUID
    context_id: UUID
    severity: str
    status: IncidentStatus
    detected_at: datetime
    created_at: datetime
    updated_at: datetime
    primary_detection_id: Optional[UUID] = None
    assigned_to: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None