from dataclasses import dataclass


@dataclass
class AssistantContext:
    incident_id: str
    category: str
    risk_score: float
    confidence: float
    explanation: str


@dataclass
class AssistantResponse:
    message: str