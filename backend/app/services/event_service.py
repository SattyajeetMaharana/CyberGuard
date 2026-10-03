from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.event import Event


async def create_event(
    db: AsyncSession,
    *,
    event_type: str,
    source_type: str,
    context_id: UUID | None = None,
    user_id: UUID | None = None,
    device_id: UUID | None = None,
    payload: dict[str, Any] | None = None,
    occurred_at: datetime | None = None,
) -> Event:
    event = Event(
        context_id=context_id,
        user_id=user_id,
        device_id=device_id,
        event_type=event_type,
        source_type=source_type,
        payload=payload,
        occurred_at=occurred_at or datetime.now(timezone.utc),
    )

    db.add(event)
    await db.flush()

    return event
