from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_permissions
from app.db.models.employee import Employee
from app.db.models.role import Role
from app.db.models.security_context import SecurityContext
from app.schemas.employee import (
    EmployeeBulkCreateRequest,
    EmployeeBulkResult,
    EmployeeCreateRequest,
    EmployeeResponse,
    EmployeeUpdateRequest,
)
from app.services.employee_service import (
    bulk_create_employees,
    create_employee,
    get_employee,
    get_employee_by_employee_id,
    import_employees_from_csv,
    list_employees,
    remove_employee,
    suspend_employee,
    update_employee,
)

router = APIRouter(
    prefix="/organizations/{organization_id}/employees",
    tags=["Employees"],
)


async def _authorize_organization_access(
    db: AsyncSession,
    current_user,
    organization_id: UUID,
) -> None:
    role_result = await db.execute(
        select(Role.name).where(
            Role.id == current_user.role_id
        )
    )

    role_name = role_result.scalar_one_or_none()

    if role_name == "SUPER_ADMIN":
        return

    if role_name != "ORGANIZATION_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin access required.",
        )

    context_result = await db.execute(
        select(SecurityContext).where(
            SecurityContext.user_id == current_user.id,
            SecurityContext.organization_id == organization_id,
            SecurityContext.context_type == "ORGANIZATION",
            SecurityContext.is_active.is_(True),
        )
    )

    context = context_result.scalar_one_or_none()

    if context is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this organization.",
        )


def _employee_response(employee: Employee) -> EmployeeResponse:
    return EmployeeResponse(
        id=employee.id,
        employee_id=employee.employee_id,
        name=employee.name,
        email=employee.email,
        branch=employee.branch,
        organization_id=employee.organization_id,
        department_id=employee.department_id,
        user_id=employee.user_id,
        status=employee.status,
        created_at=employee.created_at.isoformat(),
        updated_at=employee.updated_at.isoformat(),
    )


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization_employee(
    organization_id: UUID,
    payload: EmployeeCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    _: None = Depends(require_permissions("users:write")),
):
    await _authorize_organization_access(
        db,
        current_user,
        organization_id,
    )

    try:
        employee = await create_employee(
            db,
            organization_id,
            payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return _employee_response(employee)


@router.post(
    "/bulk",
    response_model=EmployeeBulkResult,
    status_code=status.HTTP_201_CREATED,
)
async def bulk_create_organization_employees(
    organization_id: UUID,
    payload: EmployeeBulkCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    _: None = Depends(require_permissions("users:write")),
):
    await _authorize_organization_access(
        db,
        current_user,
        organization_id,
    )

    result = await bulk_create_employees(
        db,
        organization_id,
        payload.employees,
    )

    return {
        **result,
        "employees": [
            _employee_response(employee)
            for employee in result["employees"]
        ],
    }


@router.post(
    "/import-csv",
    response_model=EmployeeBulkResult,
    status_code=status.HTTP_201_CREATED,
)
async def import_organization_employees_csv(
    organization_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    _: None = Depends(require_permissions("users:write")),
):
    await _authorize_organization_access(
        db,
        current_user,
        organization_id,
    )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty.",
        )

    try:
        csv_content = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file must be UTF-8 encoded.",
        ) from exc

    try:
        result = await import_employees_from_csv(
            db,
            organization_id,
            csv_content,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {
        **result,
        "employees": [
            _employee_response(employee)
            for employee in result["employees"]
        ],
    }


@router.get(
    "",
    response_model=list[EmployeeResponse],
)
async def list_organization_employees(
    organization_id: UUID,
    search: str | None = Query(default=None),
    include_inactive: bool = Query(default=False),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    _: None = Depends(require_permissions("users:read")),
):
    await _authorize_organization_access(
        db,
        current_user,
        organization_id,
    )

    employees = await list_employees(
        db,
        organization_id,
        search=search,
        include_inactive=include_inactive,
    )

    return [
        _employee_response(employee)
        for employee in employees
    ]


@router.get(
    "/by-employee-id/{employee_id}",
    response_model=EmployeeResponse,
)
async def get_organization_employee_by_employee_id(
    organization_id: UUID,
    employee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    _: None = Depends(require_permissions("users:read")),
):
    await _authorize_organization_access(
        db,
        current_user,
        organization_id,
    )

    employee = await get_employee_by_employee_id(
        db,
        organization_id,
        employee_id,
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    return _employee_response(employee)


@router.get(
    "/{employee_uuid}",
    response_model=EmployeeResponse,
)
async def get_organization_employee(
    organization_id: UUID,
    employee_uuid: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    _: None = Depends(require_permissions("users:read")),
):
    await _authorize_organization_access(
        db,
        current_user,
        organization_id,
    )

    employee = await get_employee(
        db,
        organization_id,
        employee_uuid,
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    return _employee_response(employee)


@router.patch(
    "/{employee_uuid}",
    response_model=EmployeeResponse,
)
async def update_organization_employee(
    organization_id: UUID,
    employee_uuid: UUID,
    payload: EmployeeUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    _: None = Depends(require_permissions("users:write")),
):
    await _authorize_organization_access(
        db,
        current_user,
        organization_id,
    )

    try:
        employee = await update_employee(
            db,
            organization_id,
            employee_uuid,
            payload,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    return _employee_response(employee)


@router.post(
    "/{employee_uuid}/suspend",
    response_model=EmployeeResponse,
)
async def suspend_organization_employee(
    organization_id: UUID,
    employee_uuid: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    _: None = Depends(require_permissions("users:write")),
):
    await _authorize_organization_access(
        db,
        current_user,
        organization_id,
    )

    employee = await suspend_employee(
        db,
        organization_id,
        employee_uuid,
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    return _employee_response(employee)


@router.delete(
    "/{employee_uuid}",
    response_model=EmployeeResponse,
)
async def remove_organization_employee(
    organization_id: UUID,
    employee_uuid: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    _: None = Depends(require_permissions("users:delete")),
):
    await _authorize_organization_access(
        db,
        current_user,
        organization_id,
    )

    employee = await remove_employee(
        db,
        organization_id,
        employee_uuid,
    )

    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found.",
        )

    return _employee_response(employee)