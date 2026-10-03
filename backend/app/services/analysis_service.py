from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.device import Device
from app.db.models.security_context import SecurityContext
from app.db.models.user import User
from app.services.detection_context import DetectionContext
from app.services.detection_orchestrator import (
    DetectionOrchestrator,
    DetectorUnavailableError,
)
from app.services.detection_service import create_detection
from app.services.event_service import create_event
from app.pipeline.security_pipeline import SecurityPipeline
from app.scoring.service import score_service
from app.notifications.service import notification_service


async def analyze_url(
    db: AsyncSession,
    *,
    user: User,
    url: str,
    device_id: UUID | None = None,
    orchestrator: DetectionOrchestrator,
):
    context_result = await db.execute(
        select(SecurityContext).where(
            SecurityContext.user_id == user.id,
            SecurityContext.context_type == "PERSONAL",
            SecurityContext.is_active.is_(True),
        )
    )
    context = context_result.scalar_one_or_none()

    if context is None:
        raise ValueError("Active personal security context not found")

    if device_id is not None:
        device_result = await db.execute(
            select(Device).where(
                Device.id == device_id,
                Device.user_id == user.id,
                Device.is_active.is_(True),
            )
        )
        device = device_result.scalar_one_or_none()

        if device is None:
            raise ValueError("Device not found or inactive")

    event = await create_event(
        db=db,
        event_type="URL_ANALYSIS",
        source_type="url_analysis",
        context_id=context.id,
        user_id=user.id,
        device_id=device_id,
        payload={"url": url},
    )

    detector_event = {
        "event_id": str(event.id),
        "context_id": str(context.id),
        "user_id": str(user.id),
        "device_id": str(device_id) if device_id else None,
        "event_type": event.event_type,
        "source_type": event.source_type,
        "timestamp": event.occurred_at.isoformat(),
        "payload": {"url": url},
    }

    try:
        detector_result = orchestrator.analyze(detector_event)

        detection = await create_detection(
            db=db,
            event_id=event.id,
            category=detector_result.category,
            prediction=detector_result.prediction,
            risk_score=detector_result.risk_score,
            risk_level=detector_result.risk_level,
            confidence=detector_result.confidence,
            indicators=detector_result.indicators,
            explanation=detector_result.explanation,
            recommended_actions=detector_result.recommended_actions,
            model_version=detector_result.model_version,
            detector_version=detector_result.detector_version,
            target=url,
        )

        detection_context = DetectionContext(
            detection=detection,
            user_id=user.id,
            context_id=context.id,
            target=url,
        )

        security_pipeline = SecurityPipeline(
            score_service=score_service,
            notification_service=notification_service,
        )

        pipeline_result = security_pipeline.process(detection_context)

        return (
            event,
            context,
            detection,
            detection_context,
            pipeline_result,
        )

    except DetectorUnavailableError:
        await db.rollback()
        raise