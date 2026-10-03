from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.db.models.detection import Detection


@dataclass
class DetectionContext:
    detection: Detection
    user_id: UUID
    context_id: UUID
    target: str | None = None

    @property
    def id(self) -> UUID:
        return self.detection.id

    @property
    def event_id(self) -> UUID:
        return self.detection.event_id

    @property
    def category(self) -> str:
        return self.detection.category

    @property
    def risk_score(self) -> int:
        return self.detection.risk_score

    @property
    def confidence(self) -> float:
        return self.detection.confidence

    @property
    def indicators(self) -> list:
        return self.detection.indicators or []

    @property
    def recommended_actions(self) -> list:
        return self.detection.recommended_actions or []