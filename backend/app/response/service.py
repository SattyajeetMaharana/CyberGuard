from typing import Protocol, Sequence
from uuid import UUID

from .contracts import (
    ScoreDomain,
    ScoreEvent,
    ScoreEventInput,
    ScoreHistoryQuery,
    ScoreSnapshot,
    ScoreSubjectType,
)


class ScoreService(Protocol):
    def calculate_score(
        self,
        current_score: float,
        *,
        threat_detected: bool,
    ) -> float:
        """Calculate a score according to the agreed scoring version."""
        ...

    def record_score_event(self, event: ScoreEventInput) -> ScoreEvent:
        """Record a score change and return its history event."""
        ...

    def get_current_score(
        self,
        *,
        context_id: UUID,
        subject_type: ScoreSubjectType,
        subject_id: UUID,
        domain: ScoreDomain,
    ) -> ScoreSnapshot | None:
        ...

    def get_score_history(
        self,
        query: ScoreHistoryQuery,
    ) -> Sequence[ScoreEvent]:
        ...