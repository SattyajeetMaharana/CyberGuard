from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class DepartmentCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    code: str = Field(min_length=1, max_length=50)


class DepartmentUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    is_active: bool | None = None


class DepartmentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    code: str
    is_active: bool
    created_at: str
    updated_at: str

    model_config = {
        "from_attributes": True,
    }