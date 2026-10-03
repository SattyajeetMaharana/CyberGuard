from .contracts import AssistantContext


def build_context(
    incident_id: str,
    category: str,
    risk_score: float,
    confidence: float,
    explanation: str
) -> AssistantContext:

    return AssistantContext(
        incident_id=incident_id,
        category=category,
        risk_score=risk_score,
        confidence=confidence,
        explanation=explanation
    )