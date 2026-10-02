from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping, Protocol
from uuid import UUID


class JobType(StrEnum):
    NOTIFICATION = "notification"
    WARNING_ESCALATION = "warning_escalation"
    SCHEDULED_CHECK = "scheduled_check"
    SCORE_PROCESSING = "score_processing"
    CLEANUP = "cleanup"
    POLICY_CHECK = "policy_check"


@dataclass(frozen=True)
class WorkerJob:
    id: UUID
    job_type: JobType
    payload: Mapping[str, Any] = field(default_factory=dict)
    scheduled_at: datetime | None = None


class JobHandler(Protocol):
    def __call__(self, job: WorkerJob) -> None:
        ...