from __future__ import annotations

from app.assistant.context import build_context
from app.assistant.contracts import AssistantResponse
from app.assistant.service import assistant_service
from app.orchestration.service import audit_service


def assist_with_threat(
    incident_id: str,
    category: str,
    risk_score: float,
    confidence: float,
    explanation: str,
    indicators: tuple[str, ...] = (),
    incident_status: str = "UNKNOWN",
    recommended_actions: tuple[str, ...] = (),
    security_context: dict | None = None,
) -> AssistantResponse:
    context = build_context(
        incident_id=incident_id,
        category=category,
        risk_score=risk_score,
        confidence=confidence,
        explanation=explanation,
        indicators=indicators,
        incident_status=incident_status,
        recommended_actions=recommended_actions,
        security_context=security_context or {},
    )

    audit_service.record(
        actor="assistant",
        action="ASSISTANT_INVOCATION",
        target=incident_id,
        reason=f"Threat category: {context.category}",
        outcome="CONTEXT_BUILT",
    )

    response = assistant_service.respond(context)

    audit_service.record(
        actor="assistant",
        action="ASSISTANT_RECOMMENDATION",
        target=incident_id,
        reason=response.message,
        outcome="RECOMMENDATION_CREATED",
    )

    return response
