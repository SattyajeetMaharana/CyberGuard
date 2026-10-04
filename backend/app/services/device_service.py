from __future__ import annotations

import hashlib
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.device import Device


def _hash_device_identifier(device_identifier: str) -> str:
    return hashlib.sha256(
        device_identifier.encode("utf-8")
    ).hexdigest()


async def register_device(
    db: AsyncSession,
    *,
    user_id: UUID,
    organization_id: UUID | None,
    device_identifier: str,
    device_name: str | None = None,
    platform: str | None = None,
) -> Device:
    device_identifier_hash = _hash_device_identifier(device_identifier)

    existing = await db.scalar(
        select(Device).where(
            Device.device_identifier_hash == device_identifier_hash,
        )
    )

    if existing is not None:
        if (
            existing.user_id != user_id
            or existing.organization_id != organization_id
        ):
            raise ValueError("Device is already registered to another context")

        existing.device_name = device_name
        existing.platform = platform
        existing.is_active = True

        await db.commit()
        await db.refresh(existing)
        return existing

    device = Device(
        user_id=user_id,
        organization_id=organization_id,
        device_identifier_hash=device_identifier_hash,
        device_name=device_name,
        platform=platform,
        is_active=True,
    )

    db.add(device)
    await db.commit()
    await db.refresh(device)

    return device


async def list_user_devices(
    db: AsyncSession,
    *,
    user_id: UUID,
    organization_id: UUID | None = None,
) -> list[Device]:
    result = await db.execute(
        select(Device)
        .where(
            Device.user_id == user_id,
            Device.organization_id == organization_id,
        )
        .order_by(Device.created_at.desc())
    )

    return list(result.scalars().all())


async def set_device_activation(
    db: AsyncSession,
    *,
    user_id: UUID,
    device_id: UUID,
    is_active: bool,
    organization_id: UUID | None = None,
) -> Device | None:
    device = await db.scalar(
        select(Device).where(
            Device.id == device_id,
            Device.user_id == user_id,
            Device.organization_id == organization_id,
        )
    )

    if device is None:
        return None

    device.is_active = is_active

    await db.commit()
    await db.refresh(device)

    return device