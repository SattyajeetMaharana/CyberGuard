from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.organization import (
    OrganizationRegisterRequest,
    OrganizationRegisterResponse,
)
from app.services.organization_service import register_organization


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.post(
    "/register",
    response_model=OrganizationRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: OrganizationRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        organization = await register_organization(
            db=db,
            organization_email=str(payload.organization_email),
            password=payload.password,
            organization_name=payload.organization_name,
            organization_identifier=payload.organization_identifier,
            proof_type=payload.proof_type,
            proof_reference=payload.proof_reference,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return OrganizationRegisterResponse(
        organization_id=organization.id,
        organization_name=organization.name,
        organization_email=organization.organization_email,
        organization_identifier=organization.organization_identifier,
        web_id=organization.web_id,
        status=str(organization.status),
        verification_status="PENDING",
    )