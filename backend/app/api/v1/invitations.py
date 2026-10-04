from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permissions
from app.db.models.invitation import Invitation
from app.db.models.role import Role
from app.db.models.security_context import SecurityContext
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.invitation import (
    InvitationAcceptRequest,
    InvitationAcceptResponse,
    InvitationCreateRequest,
    InvitationCreateResponse,
    InvitationResponse,
)
from app.services.invitation_service import (
    accept_invitation,
    create_invitation,
    revoke_invitation,
)

router = APIRouter(
    prefix="/organizations/{organization_id}/invitations",
    tags=["Organization Invitations"],
)


async def _authorize_organization_admin(
    db: AsyncSession,
    current_user: User,
    organization_id: UUID,
) -> None:
    role_name = await db.scalar(
        select(Role.name).where(Role.id == current_user.role_id)
    )

    if role_name == "SUPER_ADMIN":
        return

    if role_name != "ORGANIZATION_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin access required",
        )

    context = await db.scalar(
        select(SecurityContext).where(
            SecurityContext.user_id == current_user.id,
            SecurityContext.organization_id == organization_id,
            SecurityContext.context_type == "ORGANIZATION",
            SecurityContext.is_active.is_(True),
        )
    )

    if context is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization access denied",
        )


@router.post(
    "",
    response_model=InvitationCreateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions("users:write"))],
)
async def create_organization_invitation(
    organization_id: UUID,
    payload: InvitationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _authorize_organization_admin(
        db,
        current_user,
        organization_id,
    )

    try:
        invitation, token = await create_invitation(
            db,
            organization_id=organization_id,
            employee_id=payload.employee_id,
            invited_by=current_user.id,
            expires_in_hours=payload.expires_in_hours,
        )

        return InvitationCreateResponse(
            id=invitation.id,
            organization_id=invitation.organization_id,
            employee_id=invitation.employee_id,
            expires_at=invitation.expires_at,
            status=invitation.status,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at,
            token=token,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/accept",
    response_model=InvitationAcceptResponse,
)
async def accept_organization_invitation(
    organization_id: UUID,
    payload: InvitationAcceptRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        invitation = await accept_invitation(
            db,
            token=payload.token,
            organization_id=organization_id,
        )

        return InvitationAcceptResponse(
            invitation_id=invitation.id,
            employee_id=invitation.employee_id,
            organization_id=invitation.organization_id,
            status=invitation.status,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/{invitation_id}/revoke",
    response_model=InvitationResponse,
    dependencies=[Depends(require_permissions("users:write"))],
)
async def revoke_organization_invitation(
    organization_id: UUID,
    invitation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _authorize_organization_admin(
        db,
        current_user,
        organization_id,
    )

    try:
        return await revoke_invitation(
            db,
            organization_id=organization_id,
            invitation_id=invitation_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc