from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    """
    Legacy-compatible event creation schema.
    Kept available so existing code does not break.
    """

    user_id: UUID | None = None
    event_type: str = Field(..., min_length=1, max_length=100)
    source: str | None = Field(default=None, max_length=100)
    payload: dict[str, Any] | None = None
    occurred_at: datetime | None = None


class EventResponse(BaseModel):
    """
    Legacy-compatible event response schema.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    event_type: str
    source: str | None = None
    payload: dict[str, Any] | None = None
    occurred_at: datetime


class CoreEventCreate(BaseModel):
    """
    Normalized CyberGuard security event accepted by the
    core Event API.

    user_id and context_id are intentionally NOT accepted
    from the client. They are derived from the authenticated
    user's security context.
    """

    event_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    source_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    device_id: UUID | None = None

    payload: dict[str, Any] = Field(
        default_factory=dict,
    )

    occurred_at: datetime | None = None


class CoreEventResponse(BaseModel):
    """
    Normalized event response.
    """

    model_config = ConfigDict(from_attributes=True)

    event_id: UUID
    context_id: UUID
    user_id: UUID
    device_id: UUID | None
    event_type: str
    source_type: str | None
    payload: dict[str, Any]
    occurred_at: datetime