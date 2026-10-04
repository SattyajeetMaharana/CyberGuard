from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.models.role import Role
from app.db.models.security_context import SecurityContext
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.device import (
    DeviceActivationRequest,
    DeviceCreate,
    DeviceResponse,
)
from app.services.device_service import (
    list_user_devices,
    register_device,
    set_device_activation,
)

router = APIRouter(prefix="/devices", tags=["Devices"])


async def _authorize_device_organization(
    db: AsyncSession,
    current_user: User,
    organization_id: UUID | None,
) -> None:
    if organization_id is None:
        return

    role_name = await db.scalar(
        select(Role.name).where(Role.id == current_user.role_id)
    )

    if role_name == "SUPER_ADMIN":
        return

    if role_name not in {
        "ORGANIZATION_ADMIN",
        "ORGANIZATION_EMPLOYEE",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization device access denied",
        )

    context = await db.scalar(
        select(SecurityContext).where(
            SecurityContext.user_id == current_user.id,
            SecurityContext.organization_id == organization_id,
            SecurityContext.context_type == "ORGANIZATION",
            SecurityContext.is_active.is_(True),
        )
    )

    if context is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization device access denied",
        )


@router.post(
    "",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_device(
    payload: DeviceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _authorize_device_organization(
        db,
        current_user,
        payload.organization_id,
    )

    return await register_device(
        db=db,
        user_id=current_user.id,
        organization_id=payload.organization_id,
        device_identifier=payload.device_identifier,
        device_name=payload.device_name,
        platform=payload.platform,
    )


@router.get(
    "",
    response_model=list[DeviceResponse],
)
async def get_devices(
    organization_id: UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _authorize_device_organization(
        db,
        current_user,
        organization_id,
    )

    return await list_user_devices(
        db=db,
        user_id=current_user.id,
        organization_id=organization_id,
    )


@router.patch(
    "/{device_id}/activation",
    response_model=DeviceResponse,
)
async def activate_device(
    device_id: UUID,
    payload: DeviceActivationRequest,
    organization_id: UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _authorize_device_organization(
        db,
        current_user,
        organization_id,
    )

    device = await set_device_activation(
        db=db,
        user_id=current_user.id,
        device_id=device_id,
        is_active=payload.is_active,
        organization_id=organization_id,
    )

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    return device