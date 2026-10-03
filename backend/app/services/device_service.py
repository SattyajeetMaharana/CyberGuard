from __future__ import annotations

from hashlib import sha256
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.device import Device


def hash_device_identifier(device_identifier: str) -> str:
    return sha256(device_identifier.encode("utf-8")).hexdigest()


async def get_user_device(
    db: AsyncSession,
    *,
    user_id: UUID,
    device_identifier: str,
) -> Device | None:
    identifier_hash = hash_device_identifier(device_identifier)

    result = await db.execute(
        select(Device).where(
            Device.user_id == user_id,
            Device.device_identifier_hash == identifier_hash,
        )
    )

    return result.scalar_one_or_none()


async def register_device(
    db: AsyncSession,
    *,
    user_id: UUID,
    device_identifier: str,
    device_name: str | None = None,
    platform: str | None = None,
) -> Device:
    identifier_hash = hash_device_identifier(device_identifier)

    result = await db.execute(
        select(Device).where(
            Device.user_id == user_id,
            Device.device_identifier_hash == identifier_hash,
        )
    )
    device = result.scalar_one_or_none()

    if device is not None:
        if device_name is not None:
            device.device_name = device_name
        if platform is not None:
            device.platform = platform

        device.is_active = True
        await db.commit()
        await db.refresh(device)
        return device

    device = Device(
        user_id=user_id,
        device_identifier_hash=identifier_hash,
        device_name=device_name,
        platform=platform,
        is_active=True,
    )

    db.add(device)
    await db.commit()
    await db.refresh(device)

    return device


async def set_device_activation(
    db: AsyncSession,
    *,
    user_id: UUID,
    device_id: UUID,
    is_active: bool,
) -> Device | None:
    result = await db.execute(
        select(Device).where(
            Device.id == device_id,
            Device.user_id == user_id,
        )
    )

    device = result.scalar_one_or_none()

    if device is None:
        return None

    device.is_active = is_active

    await db.commit()
    await db.refresh(device)

    return device


async def list_user_devices(
    db: AsyncSession,
    *,
    user_id: UUID,
) -> list[Device]:
    result = await db.execute(
        select(Device)
        .where(Device.user_id == user_id)
        .order_by(Device.created_at.desc())
    )

    return list(result.scalars().all())
