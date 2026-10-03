from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.detection import Detection


async def create_detection(
    db: AsyncSession,
    *,
    event_id: UUID,
    category: str,
    prediction: str,
    risk_score: float,
    risk_level: str,
    confidence: float,
    indicators: list[str] | None = None,
    explanation: str = "",
    recommended_actions: list[str] | None = None,
    model_version: str = "",
    detector_version: str = "",
    target: str | None = None,
) -> Detection:
    xai_information = {
        "prediction": prediction,
        "explanation": explanation,
    }

    if target is not None:
        xai_information["target"] = target

    detection = Detection(
        event_id=event_id,
        category=category,
        risk_level=risk_level,
        risk_score=int(round(risk_score)),
        confidence=confidence,
        xai_information=xai_information,
        indicators=indicators or [],
        recommended_actions=recommended_actions or [],
        status="active",
        detector_version=detector_version or None,
        model_version=model_version or None,
    )

    db.add(detection)
    await db.flush()

    return detection