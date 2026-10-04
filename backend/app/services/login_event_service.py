from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.login_event import LoginEvent


async def record_login_event(
    db: AsyncSession,
    *,
    user_id: UUID,
    organization_id: UUID | None,
    device_id: UUID | None,
    login_success: bool,
    ip_address: str | None = None,
    user_agent: str | None = None,
    occurred_at: datetime | None = None,
) -> LoginEvent:
    event = LoginEvent(
        user_id=user_id,
        organization_id=organization_id,
        device_id=device_id,
        occurred_at=occurred_at or datetime.now(timezone.utc),
        login_success=login_success,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    db.add(event)
    await db.commit()
    await db.refresh(event)

    return event


async def list_login_events(
    db: AsyncSession,
    *,
    user_id: UUID,
    organization_id: UUID | None = None,
) -> list[LoginEvent]:
    query = select(LoginEvent).where(
        LoginEvent.user_id == user_id,
    )

    if organization_id is not None:
        query = query.where(
            LoginEvent.organization_id == organization_id,
        )

    query = query.order_by(LoginEvent.occurred_at.desc())

    result = await db.execute(query)

    return list(result.scalars().all())