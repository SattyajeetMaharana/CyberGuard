from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permissions
from app.db.models.role import Role
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.organization import (
    OrganizationVerificationDecisionRequest,
    OrganizationVerificationResponse,
)
from app.services.organization_verification_service import (
    approve_organization,
    get_organization_verification,
    list_pending_organizations,
    reject_organization,
    suspend_organization,
)


router = APIRouter(
    prefix="/admin/organizations",
    tags=["Admin - Organizations"],
)


async def _require_super_admin(
    current_user: User,
    db: AsyncSession,
) -> User:
    if current_user.role_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required",
        )

    result = await db.execute(
        select(Role.name).where(Role.id == current_user.role_id)
    )

    role_name = result.scalar_one_or_none()

    if role_name != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super Admin access required",
        )

    return current_user


def _to_response(
    organization,
    verification,
) -> OrganizationVerificationResponse:
    return OrganizationVerificationResponse(
        organization_id=organization.id,
        organization_name=organization.name,
        organization_email=organization.organization_email,
        organization_identifier=organization.organization_identifier,
        web_id=organization.web_id,
        organization_status=organization.status.value,
        verification_status=verification.status.value,
        proof_type=verification.proof_type,
        proof_reference=verification.proof_reference,
        reviewed_by=verification.reviewed_by,
        review_notes=verification.review_notes,
        created_at=organization.created_at.isoformat(),
        updated_at=organization.updated_at.isoformat(),
    )


@router.get(
    "/pending",
    response_model=list[OrganizationVerificationResponse],
)
async def get_pending_organizations(
    current_user: User = Depends(
        require_permissions("security:manage")
    ),
    db: AsyncSession = Depends(get_db),
):
    await _require_super_admin(current_user, db)

    records = await list_pending_organizations(db)

    return [
        _to_response(organization, verification)
        for organization, verification in records
    ]


@router.get(
    "/{organization_id}/verification",
    response_model=OrganizationVerificationResponse,
)
async def get_verification(
    organization_id: UUID,
    current_user: User = Depends(
        require_permissions("security:manage")
    ),
    db: AsyncSession = Depends(get_db),
):
    await _require_super_admin(current_user, db)

    record = await get_organization_verification(
        db,
        organization_id,
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization verification record not found",
        )

    organization, verification = record

    return _to_response(organization, verification)


@router.patch(
    "/{organization_id}/approve",
    response_model=OrganizationVerificationResponse,
)
async def approve(
    organization_id: UUID,
    payload: OrganizationVerificationDecisionRequest,
    current_user: User = Depends(
        require_permissions("security:manage")
    ),
    db: AsyncSession = Depends(get_db),
):
    await _require_super_admin(current_user, db)

    record = await approve_organization(
        db=db,
        organization_id=organization_id,
        reviewed_by=current_user.id,
        review_notes=payload.review_notes,
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization verification record not found",
        )

    organization, verification = record

    return _to_response(organization, verification)


@router.patch(
    "/{organization_id}/reject",
    response_model=OrganizationVerificationResponse,
)
async def reject(
    organization_id: UUID,
    payload: OrganizationVerificationDecisionRequest,
    current_user: User = Depends(
        require_permissions("security:manage")
    ),
    db: AsyncSession = Depends(get_db),
):
    await _require_super_admin(current_user, db)

    record = await reject_organization(
        db=db,
        organization_id=organization_id,
        reviewed_by=current_user.id,
        review_notes=payload.review_notes,
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization verification record not found",
        )

    organization, verification = record

    return _to_response(organization, verification)


@router.patch(
    "/{organization_id}/suspend",
    response_model=OrganizationVerificationResponse,
)
async def suspend(
    organization_id: UUID,
    payload: OrganizationVerificationDecisionRequest,
    current_user: User = Depends(
        require_permissions("security:manage")
    ),
    db: AsyncSession = Depends(get_db),
):
    await _require_super_admin(current_user, db)

    record = await suspend_organization(
        db=db,
        organization_id=organization_id,
        reviewed_by=current_user.id,
        review_notes=payload.review_notes,
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization verification record not found",
        )

    organization, verification = record

    return _to_response(organization, verification)