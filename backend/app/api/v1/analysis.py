from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permissions
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.analysis import AnalysisResponse, URLAnalysisRequest
from app.services.analysis_service import analyze_url
from app.services.detection_orchestrator import DetectorUnavailableError
from app.services.detection_orchestrator import DetectionOrchestrator
from app.services.url_detector import MaliciousURLDetector


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


def create_url_detection_orchestrator() -> DetectionOrchestrator:
    """
    Create the production URL detection orchestrator.

    The ML predictor is initialized lazily when the adapter is created.
    """

    return DetectionOrchestrator(
        detector=MaliciousURLDetector(),
    )


@router.post(
    "/url",
    response_model=AnalysisResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_url_endpoint(
    payload: URLAnalysisRequest,
    current_user: User = Depends(
        require_permissions("security:analyze")
    ),
    db: AsyncSession = Depends(get_db),
):
    try:
        orchestrator = create_url_detection_orchestrator()

        (
            event,
            context,
            detection,
            detection_context,
            pipeline_result,
        ) = await analyze_url(
            db=db,
            user=current_user,
            url=str(payload.url),
            device_id=payload.device_id,
            orchestrator=orchestrator,
        )

    except DetectorUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="URL detection service is currently unavailable",
        ) from exc

    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="URL detection model is currently unavailable",
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    xai_information = detection.xai_information or {}

    recommendations = (
        pipeline_result.recommendations or []
    )

    recommended_actions = [
        recommendation.action.value
        for recommendation in recommendations
    ]

    primary_recommendation = (
        recommended_actions[0]
        if recommended_actions
        else None
    )

    incident = None

    if pipeline_result.incident_created:
        incident_status = pipeline_result.incident_status

        if hasattr(incident_status, "value"):
            incident_status = incident_status.value

        incident = {
            "created": pipeline_result.incident_created,
            "status": incident_status,
            "correlation_key": pipeline_result.correlation_key,
        }

    await db.commit()

    return AnalysisResponse(
        event_id=event.id,
        detection_id=detection.id,
        category=detection.category,
        prediction=str(
            xai_information.get(
                "prediction",
                detection.category,
            )
        ),
        risk_score=float(detection.risk_score),
        risk_level=detection.risk_level,
        confidence=float(detection.confidence),
        indicators=detection.indicators or [],
        explanation=str(
            xai_information.get(
                "explanation",
                "",
            )
        ),
        recommended_actions=recommended_actions,
        incident=incident,
        cyber_score=pipeline_result.cyber_score,
        recommended_action=primary_recommendation,
    )