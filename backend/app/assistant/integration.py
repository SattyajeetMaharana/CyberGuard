from __future__ import annotations

from typing import Any, Mapping, Sequence

from .context import build_context
from .contracts import AssistantContext, AssistantResponse
from .service import assistant_service
from .response import create_approval_request


def assist_with_threat(
    *,
    incident_id: str,
    category: str,
    risk_score: float,
    confidence: float,
    explanation: str = "",
    indicators: Sequence[str] | None = None,
    incident_status: str = "UNKNOWN",
    recommended_actions: Sequence[str] | None = None,
    security_context: Mapping[str, Any] | None = None,
) -> tuple[AssistantContext, AssistantResponse]:

    context = build_context(
        incident_id=incident_id,
        category=category,
        risk_score=risk_score,
        confidence=confidence,
        explanation=explanation,
        indicators=indicators,
        incident_status=incident_status,
        recommended_actions=recommended_actions,
        security_context=security_context,
    )

    response = assistant_service.respond(context)

    return context, response


def recommend_approval(
    *,
    context: AssistantContext,
    action: str,
    reason: str,
):
    return create_approval_request(
        incident_id=context.incident_id,
        context=context,
        action=action,
        reason=reason,
    )
