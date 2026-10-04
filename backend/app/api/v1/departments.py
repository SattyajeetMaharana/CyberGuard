from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_permissions
from app.db.models.role import Role
from app.db.models.security_context import SecurityContext
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.department import (
    DepartmentCreateRequest,
    DepartmentResponse,
    DepartmentUpdateRequest,
)
from app.services.department_service import (
    create_department,
    delete_department,
    get_department,
    list_departments,
    update_department,
)


router = APIRouter(
    prefix="/organizations/{organization_id}/departments",
    tags=["Departments"],
)


async def _authorize_organization_admin(
    current_user: User,
    organization_id: UUID,
    db: AsyncSession,
) -> None:
    if current_user.role_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization administrator access required",
        )

    role_result = await db.execute(
        select(Role.name).where(Role.id == current_user.role_id)
    )

    role_name = role_result.scalar_one_or_none()

    if role_name == "SUPER_ADMIN":
        return

    if role_name != "ORGANIZATION_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization administrator access required",
        )

    context_result = await db.execute(
        select(SecurityContext.id).where(
            SecurityContext.user_id == current_user.id,
            SecurityContext.organization_id == organization_id,
            SecurityContext.context_type == "ORGANIZATION",
            SecurityContext.is_active.is_(True),
        )
    )

    if context_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization access denied",
        )


def _to_response(department) -> DepartmentResponse:
    return DepartmentResponse(
        id=department.id,
        organization_id=department.organization_id,
        name=department.name,
        code=department.code,
        is_active=department.is_active,
        created_at=department.created_at.isoformat(),
        updated_at=department.updated_at.isoformat(),
    )


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create(
    organization_id: UUID,
    payload: DepartmentCreateRequest,
    current_user: User = Depends(
        require_permissions("users:write")
    ),
    db: AsyncSession = Depends(get_db),
):
    await _authorize_organization_admin(
        current_user,
        organization_id,
        db,
    )

    try:
        department = await create_department(
            db,
            organization_id=organization_id,
            name=payload.name,
            code=payload.code,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return _to_response(department)


@router.get(
    "",
    response_model=list[DepartmentResponse],
)
async def list_all(
    organization_id: UUID,
    current_user: User = Depends(
        require_permissions("users:read")
    ),
    db: AsyncSession = Depends(get_db),
):
    await _authorize_organization_admin(
        current_user,
        organization_id,
        db,
    )

    departments = await list_departments(
        db,
        organization_id=organization_id,
    )

    return [_to_response(department) for department in departments]


@router.get(
    "/{department_id}",
    response_model=DepartmentResponse,
)
async def retrieve(
    organization_id: UUID,
    department_id: UUID,
    current_user: User = Depends(
        require_permissions("users:read")
    ),
    db: AsyncSession = Depends(get_db),
):
    await _authorize_organization_admin(
        current_user,
        organization_id,
        db,
    )

    department = await get_department(
        db,
        organization_id=organization_id,
        department_id=department_id,
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    return _to_response(department)


@router.patch(
    "/{department_id}",
    response_model=DepartmentResponse,
)
async def update(
    organization_id: UUID,
    department_id: UUID,
    payload: DepartmentUpdateRequest,
    current_user: User = Depends(
        require_permissions("users:write")
    ),
    db: AsyncSession = Depends(get_db),
):
    await _authorize_organization_admin(
        current_user,
        organization_id,
        db,
    )

    try:
        department = await update_department(
            db,
            organization_id=organization_id,
            department_id=department_id,
            name=payload.name,
            code=payload.code,
            is_active=payload.is_active,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    return _to_response(department)


@router.delete(
    "/{department_id}",
    response_model=DepartmentResponse,
)
async def delete(
    organization_id: UUID,
    department_id: UUID,
    current_user: User = Depends(
        require_permissions("users:delete")
    ),
    db: AsyncSession = Depends(get_db),
):
    await _authorize_organization_admin(
        current_user,
        organization_id,
        db,
    )

    department = await delete_department(
        db,
        organization_id=organization_id,
        department_id=department_id,
    )

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found",
        )

    return _to_response(department)