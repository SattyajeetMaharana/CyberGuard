from enum import Enum


class RiskLevel(str, Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


def risk_level_from_score(score: float) -> RiskLevel:
    if not 0 <= score <= 100:
        raise ValueError("risk score must be between 0 and 100")

    if score < 20:
        return RiskLevel.SAFE
    if score < 40:
        return RiskLevel.LOW
    if score < 60:
        return RiskLevel.MEDIUM
    if score < 80:
        return RiskLevel.HIGH

    return RiskLevel.CRITICAL
