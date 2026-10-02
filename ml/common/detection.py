from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class Detection:
    category: str
    prediction: str
    risk_score: float
    risk_level: str
    confidence: float
    indicators: list[str] = field(default_factory=list)
    explanation: str = ""
    recommended_actions: list[str] = field(default_factory=list)
    model_version: str = ""


class Detector(Protocol):
    def analyze(self, event: dict) -> Detection:
        ...
