from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permissions
from app.db.models.role import Role
from app.db.models.security_context_membership import SecurityContextMembership
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.security_context import (
    SecurityContextMembershipResponse,
    SecurityContextResponse,
)
from app.services.security_context_service import (
    add_employee_membership,
    create_organization_context,
    get_memberships,
    get_organization_context,
)

router = APIRouter(
    prefix="/organizations/{organization_id}/security-contexts",
    tags=["Security Contexts"],
)


async def _authorize_organization_access(
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

    context = await get_organization_context(
        db,
        user_id=current_user.id,
        organization_id=organization_id,
    )

    if context is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization access denied",
        )


@router.get(
    "",
    response_model=SecurityContextResponse,
    dependencies=[Depends(require_permissions("security:read"))],
)
async def get_security_context(
    organization_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _authorize_organization_access(
        db,
        current_user,
        organization_id,
    )

    context = await get_organization_context(
        db,
        user_id=current_user.id,
        organization_id=organization_id,
    )

    if context is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization security context not found",
        )

    return context


@router.post(
    "/memberships/{employee_id}",
    response_model=SecurityContextMembershipResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions("security:manage"))],
)
async def create_security_context_membership(
    organization_id: UUID,
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _authorize_organization_access(
        db,
        current_user,
        organization_id,
    )

    context = await get_organization_context(
        db,
        user_id=current_user.id,
        organization_id=organization_id,
    )

    if context is None:
        context = await create_organization_context(
            db,
            user_id=current_user.id,
            organization_id=organization_id,
        )

    try:
        return await add_employee_membership(
            db,
            context_id=context.id,
            organization_id=organization_id,
            employee_id=employee_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/memberships",
    response_model=list[SecurityContextMembershipResponse],
    dependencies=[Depends(require_permissions("security:read"))],
)
async def list_security_context_memberships(
    organization_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await _authorize_organization_access(
        db,
        current_user,
        organization_id,
    )

    context = await get_organization_context(
        db,
        user_id=current_user.id,
        organization_id=organization_id,
    )

    if context is None:
        return []

    return await get_memberships(
        db,
        context_id=context.id,
        organization_id=organization_id,
    )