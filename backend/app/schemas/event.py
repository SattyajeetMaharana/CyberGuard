from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EventCreate(BaseModel):
    user_id: UUID | None = None
    event_type: str
    source: str | None = None
    payload: dict[str, Any] | None = None
    occurred_at: datetime


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID | None = None
    event_type: str
    source: str | None = None
    payload: dict[str, Any] | None = None
    occurred_at: datetime