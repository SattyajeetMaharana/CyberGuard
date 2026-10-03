from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .contracts import AssistantContext


_SENSITIVE_KEYS = {
    "password",
    "passwd",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "apikey",
    "private_key",
    "credential",
    "authorization",
    "cookie",
}


def _sanitize_mapping(
    data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if not data:
        return {}

    safe: dict[str, Any] = {}

    for key, value in data.items():
        normalized = str(key).strip().lower()

        if normalized in _SENSITIVE_KEYS:
            safe[str(key)] = "[REDACTED]"
            continue

        if isinstance(value, Mapping):
            safe[str(key)] = _sanitize_mapping(value)
        elif isinstance(value, (list, tuple)):
            safe[str(key)] = [
                "[REDACTED]"
                if str(key).strip().lower() in _SENSITIVE_KEYS
                else item
                for item in value
            ]
        else:
            safe[str(key)] = value

    return safe


def _risk_level(score: float) -> str:
    if not 0 <= score <= 100:
        raise ValueError("risk_score must be between 0 and 100")

    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    if score >= 20:
        return "LOW"
    return "SAFE"


def build_context(
    incident_id: str,
    category: str,
    risk_score: float,
    confidence: float,
    explanation: str = "",
    *,
    indicators: Sequence[str] | None = None,
    incident_status: str = "UNKNOWN",
    recommended_actions: Sequence[str] | None = None,
    security_context: Mapping[str, Any] | None = None,
) -> AssistantContext:

    if not 0 <= confidence <= 1:
        raise ValueError("confidence must be between 0 and 1")

    safe_indicators = tuple(
        str(item)
        for item in (indicators or ())
    )

    safe_actions = tuple(
        str(item)
        for item in (recommended_actions or ())
    )

    return AssistantContext(
        incident_id=str(incident_id),
        category=str(category),
        risk_score=float(risk_score),
        risk_level=_risk_level(float(risk_score)),
        confidence=float(confidence),
        indicators=safe_indicators,
        xai_summary=str(explanation or ""),
        incident_status=str(incident_status),
        recommended_actions=safe_actions,
        security_context=_sanitize_mapping(security_context),
    )
