from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class DetectorResult:
    category: str
    prediction: str
    risk_score: float
    risk_level: str
    confidence: float
    indicators: list[str] = field(default_factory=list)
    explanation: str = ""
    recommended_actions: list[str] = field(default_factory=list)
    model_version: str = ""
    detector_version: str = ""


class URLDetector(Protocol):
    def analyze(self, event: dict[str, Any]) -> DetectorResult:
        ...


class DetectorUnavailableError(RuntimeError):
    """Raised when the production URL detector is not available."""


class DetectionOrchestrator:
    def __init__(self, detector: URLDetector | None = None):
        self.detector = detector

    def analyze(self, event: dict[str, Any]) -> DetectorResult:
        if self.detector is None:
            raise DetectorUnavailableError(
                "URL detection service is not configured"
            )

        return self.detector.analyze(event)
