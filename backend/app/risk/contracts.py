from dataclasses import dataclass
from enum import StrEnum


class RiskLevel(StrEnum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class RiskResult:
    risk_score: float
    confidence: float
    category: str
    indicators: list[str]
    level: RiskLevel