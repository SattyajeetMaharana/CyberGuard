from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.db.models.employee import EmployeeStatus


class EmployeeCreateRequest(BaseModel):
    employee_id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    branch: str | None = Field(default=None, max_length=200)
    department_id: UUID | None = None


class EmployeeUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    email: EmailStr | None = None
    branch: str | None = Field(default=None, max_length=200)
    department_id: UUID | None = None


class EmployeeResponse(BaseModel):
    id: UUID
    employee_id: str
    name: str
    email: EmailStr
    branch: str | None
    organization_id: UUID
    department_id: UUID | None
    user_id: UUID | None
    status: EmployeeStatus
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class EmployeeBulkCreateRequest(BaseModel):
    employees: list[EmployeeCreateRequest] = Field(
        min_length=1,
        max_length=1000,
    )


class EmployeeBulkResult(BaseModel):
    total: int
    created: int
    skipped: int
    failed: int
    errors: list[dict]
    employees: list[EmployeeResponse]