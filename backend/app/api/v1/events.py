from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permissions
from app.db.models.device import Device
from app.db.models.security_context import SecurityContext
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.event import CoreEventCreate, CoreEventResponse
from app.services.event_service import create_event


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post(
    "",
    response_model=CoreEventResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_core_event(
    payload: CoreEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_permissions("security:analyze")
    ),
) -> CoreEventResponse:
    """
    Create a normalized CyberGuard security event.

    Security rules:
    - Authentication is required.
    - security:analyze permission is required.
    - The authenticated user's active security context is used.
    - user_id cannot be impersonated through the request body.
    - A supplied device must belong to the authenticated user.
    """

    context_result = await db.execute(
        select(SecurityContext).where(
            SecurityContext.user_id == current_user.id,
            SecurityContext.context_type == "PERSONAL",
            SecurityContext.is_active.is_(True),
        )
    )

    context = context_result.scalar_one_or_none()

    if context is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active personal security context not found",
        )

    if payload.device_id is not None:
        device_result = await db.execute(
            select(Device).where(
                Device.id == payload.device_id,
                Device.user_id == current_user.id,
                Device.is_active.is_(True),
            )
        )

        device = device_result.scalar_one_or_none()

        if device is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Device not found or inactive",
            )

    occurred_at = payload.occurred_at

    if occurred_at is None:
        occurred_at = datetime.now(timezone.utc)
    elif occurred_at.tzinfo is None:
        occurred_at = occurred_at.replace(tzinfo=timezone.utc)
    else:
        occurred_at = occurred_at.astimezone(timezone.utc)

    event = await create_event(
        db=db,
        event_type=payload.event_type,
        source_type=payload.source_type,
        context_id=context.id,
        user_id=current_user.id,
        device_id=payload.device_id,
        payload=payload.payload,
        occurred_at=occurred_at,
    )

    await db.commit()
    await db.refresh(event)

    return CoreEventResponse(
        event_id=event.id,
        context_id=context.id,
        user_id=current_user.id,
        device_id=event.device_id,
        event_type=event.event_type,
        source_type=event.source_type,
        payload=event.payload or {},
        occurred_at=event.occurred_at,
    )