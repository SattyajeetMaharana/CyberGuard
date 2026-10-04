from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class OrganizationRegisterRequest(BaseModel):
    organization_email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    organization_name: str = Field(min_length=2, max_length=200)
    organization_identifier: str = Field(
        min_length=2,
        max_length=100,
    )
    proof_type: str | None = Field(
        default=None,
        max_length=100,
    )
    proof_reference: str | None = Field(
        default=None,
        max_length=2000,
    )


class OrganizationRegisterResponse(BaseModel):
    organization_id: UUID
    organization_name: str
    organization_email: EmailStr
    organization_identifier: str
    web_id: str
    status: str
    verification_status: str

    model_config = {
        "from_attributes": True,
    }


class OrganizationVerificationResponse(BaseModel):
    organization_id: UUID
    organization_name: str
    organization_email: EmailStr
    organization_identifier: str
    web_id: str
    organization_status: str
    verification_status: str
    proof_type: str | None
    proof_reference: str | None
    reviewed_by: UUID | None
    review_notes: str | None
    created_at: str
    updated_at: str


class OrganizationVerificationDecisionRequest(BaseModel):
    review_notes: str | None = Field(
        default=None,
        max_length=2000,
    )