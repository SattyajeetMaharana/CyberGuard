from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
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
    return await register_device(
        db=db,
        user_id=current_user.id,
        device_identifier=payload.device_identifier,
        device_name=payload.device_name,
        platform=payload.platform,
    )


@router.get(
    "",
    response_model=list[DeviceResponse],
)
async def get_devices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await list_user_devices(
        db=db,
        user_id=current_user.id,
    )


@router.patch(
    "/{device_id}/activation",
    response_model=DeviceResponse,
)
async def activate_device(
    device_id: UUID,
    payload: DeviceActivationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    device = await set_device_activation(
        db=db,
        user_id=current_user.id,
        device_id=device_id,
        is_active=payload.is_active,
    )

    if device is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found",
        )

    return device
