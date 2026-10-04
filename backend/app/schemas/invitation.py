from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.models.invitation import InvitationStatus


class InvitationCreateRequest(BaseModel):
    employee_id: UUID
    expires_in_hours: int = Field(default=72, ge=1, le=168)


class InvitationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    employee_id: UUID
    expires_at: datetime
    status: InvitationStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InvitationCreateResponse(InvitationResponse):
    token: str


class InvitationAcceptRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)


class InvitationAcceptResponse(BaseModel):
    invitation_id: UUID
    employee_id: UUID
    organization_id: UUID
    status: InvitationStatus