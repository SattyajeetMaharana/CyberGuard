from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class SecurityContextCreateRequest(BaseModel):
    context_type: str = Field(default="ORGANIZATION", min_length=1, max_length=30)


class SecurityContextResponse(BaseModel):
    id: UUID
    context_type: str
    user_id: UUID
    organization_id: UUID | None
    is_active: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class SecurityContextMembershipResponse(BaseModel):
    id: UUID
    security_context_id: UUID
    organization_id: UUID
    employee_id: UUID | None
    is_active: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}