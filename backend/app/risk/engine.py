from .contracts import RiskLevel, RiskResult


def classify_risk(score: float) -> RiskLevel:
    if not 0 <= score <= 100:
        raise ValueError("Risk score must be between 0 and 100")

    if score < 20:
        return RiskLevel.SAFE
    if score < 40:
        return RiskLevel.LOW
    if score < 60:
        return RiskLevel.MEDIUM
    if score < 80:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def evaluate_risk(detection) -> RiskResult:
    score = float(detection.risk_score)
    confidence = float(detection.confidence)

    if not 0 <= confidence <= 1:
        raise ValueError("Confidence must be between 0 and 1")

    indicators = list(getattr(detection, "indicators", []))

    return RiskResult(
        risk_score=score,
        confidence=confidence,
        category=detection.category,
        indicators=indicators,
        level=classify_risk(score),
    )