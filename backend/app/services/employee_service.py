from __future__ import annotations

import csv
import io
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.department import Department
from app.db.models.employee import Employee, EmployeeStatus
from app.schemas.employee import EmployeeCreateRequest


async def _validate_department(
    db: AsyncSession,
    organization_id: UUID,
    department_id: UUID | None,
) -> Department | None:
    if department_id is None:
        return None

    result = await db.execute(
        select(Department).where(
            Department.id == department_id,
            Department.organization_id == organization_id,
            Department.is_active.is_(True),
        )
    )

    department = result.scalar_one_or_none()

    if department is None:
        raise ValueError(
            "Department does not belong to the organization or is inactive."
        )

    return department


async def _resolve_department(
    db: AsyncSession,
    organization_id: UUID,
    department_value: str | None,
) -> UUID | None:
    if department_value is None or not department_value.strip():
        return None

    value = department_value.strip()

    result = await db.execute(
        select(Department).where(
            Department.organization_id == organization_id,
            Department.is_active.is_(True),
            or_(
                Department.code == value,
                Department.name == value,
            ),
        )
    )

    department = result.scalar_one_or_none()

    if department is None:
        raise ValueError(
            f"Department '{value}' does not exist or is inactive "
            "in this organization."
        )

    return department.id


async def create_employee(
    db: AsyncSession,
    organization_id: UUID,
    employee_data: EmployeeCreateRequest,
) -> Employee:
    await _validate_department(
        db,
        organization_id,
        employee_data.department_id,
    )

    email = str(employee_data.email).strip().lower()
    employee_id = employee_data.employee_id.strip()

    duplicate_result = await db.execute(
        select(Employee).where(
            Employee.organization_id == organization_id,
            or_(
                Employee.employee_id == employee_id,
                Employee.email == email,
            ),
        )
    )

    duplicate = duplicate_result.scalar_one_or_none()

    if duplicate is not None:
        if duplicate.employee_id == employee_id:
            raise ValueError(
                f"Employee ID '{employee_id}' already exists."
            )

        raise ValueError(
            f"Employee email '{email}' already exists."
        )

    employee = Employee(
        employee_id=employee_id,
        name=employee_data.name.strip(),
        email=email,
        branch=(
            employee_data.branch.strip()
            if employee_data.branch
            else None
        ),
        organization_id=organization_id,
        department_id=employee_data.department_id,
        status=EmployeeStatus.ACTIVE,
    )

    db.add(employee)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("Employee ID or email already exists.")

    await db.refresh(employee)
    return employee


async def list_employees(
    db: AsyncSession,
    organization_id: UUID,
    search: str | None = None,
    include_inactive: bool = False,
) -> list[Employee]:
    query = select(Employee).where(
        Employee.organization_id == organization_id
    )

    if not include_inactive:
        query = query.where(
            Employee.status == EmployeeStatus.ACTIVE
        )

    if search:
        search_value = f"%{search.strip()}%"

        query = query.where(
            or_(
                Employee.employee_id.ilike(search_value),
                Employee.name.ilike(search_value),
                Employee.email.ilike(search_value),
            )
        )

    query = query.order_by(Employee.name.asc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_employee(
    db: AsyncSession,
    organization_id: UUID,
    employee_uuid: UUID,
) -> Employee | None:
    result = await db.execute(
        select(Employee).where(
            Employee.id == employee_uuid,
            Employee.organization_id == organization_id,
        )
    )

    return result.scalar_one_or_none()


async def get_employee_by_employee_id(
    db: AsyncSession,
    organization_id: UUID,
    employee_id: str,
) -> Employee | None:
    result = await db.execute(
        select(Employee).where(
            Employee.organization_id == organization_id,
            Employee.employee_id == employee_id,
        )
    )

    return result.scalar_one_or_none()


async def update_employee(
    db: AsyncSession,
    organization_id: UUID,
    employee_uuid: UUID,
    employee_data,
) -> Employee | None:
    employee = await get_employee(
        db,
        organization_id,
        employee_uuid,
    )

    if employee is None:
        return None

    if employee_data.department_id is not None:
        await _validate_department(
            db,
            organization_id,
            employee_data.department_id,
        )

    if employee_data.email is not None:
        email = str(employee_data.email).strip().lower()

        duplicate_result = await db.execute(
            select(Employee).where(
                Employee.organization_id == organization_id,
                Employee.email == email,
                Employee.id != employee_uuid,
            )
        )

        if duplicate_result.scalar_one_or_none() is not None:
            raise ValueError(
                f"Employee email '{email}' already exists."
            )

        employee.email = email

    if employee_data.name is not None:
        employee.name = employee_data.name.strip()

    if employee_data.branch is not None:
        employee.branch = employee_data.branch.strip()

    if employee_data.department_id is not None:
        employee.department_id = employee_data.department_id

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError(
            "Employee update violates a uniqueness constraint."
        )

    await db.refresh(employee)
    return employee


async def suspend_employee(
    db: AsyncSession,
    organization_id: UUID,
    employee_uuid: UUID,
) -> Employee | None:
    employee = await get_employee(
        db,
        organization_id,
        employee_uuid,
    )

    if employee is None:
        return None

    employee.status = EmployeeStatus.SUSPENDED

    await db.commit()
    await db.refresh(employee)

    return employee


async def remove_employee(
    db: AsyncSession,
    organization_id: UUID,
    employee_uuid: UUID,
) -> Employee | None:
    employee = await get_employee(
        db,
        organization_id,
        employee_uuid,
    )

    if employee is None:
        return None

    employee.status = EmployeeStatus.REMOVED

    await db.commit()
    await db.refresh(employee)

    return employee


async def bulk_create_employees(
    db: AsyncSession,
    organization_id: UUID,
    employees: list[EmployeeCreateRequest],
) -> dict:
    total = len(employees)
    created = 0
    skipped = 0
    failed = 0
    errors: list[dict] = []
    created_employees: list[Employee] = []

    seen_employee_ids: set[str] = set()
    seen_emails: set[str] = set()

    for index, employee_data in enumerate(employees, start=1):
        employee_id = employee_data.employee_id.strip()
        email = str(employee_data.email).strip().lower()

        if employee_id in seen_employee_ids:
            skipped += 1
            errors.append(
                {
                    "row": index,
                    "employee_id": employee_id,
                    "email": email,
                    "error": "Duplicate employee ID in import.",
                }
            )
            continue

        if email in seen_emails:
            skipped += 1
            errors.append(
                {
                    "row": index,
                    "employee_id": employee_id,
                    "email": email,
                    "error": "Duplicate email in import.",
                }
            )
            continue

        seen_employee_ids.add(employee_id)
        seen_emails.add(email)

        try:
            employee = await create_employee(
                db,
                organization_id,
                employee_data,
            )

            created += 1
            created_employees.append(employee)

        except ValueError as exc:
            failed += 1
            errors.append(
                {
                    "row": index,
                    "employee_id": employee_id,
                    "email": email,
                    "error": str(exc),
                }
            )

    return {
        "total": total,
        "created": created,
        "skipped": skipped,
        "failed": failed,
        "errors": errors,
        "employees": created_employees,
    }


async def import_employees_from_csv(
    db: AsyncSession,
    organization_id: UUID,
    csv_content: str,
) -> dict:
    required_columns = {
        "email",
        "employee_name",
        "employee_id",
        "branch",
        "department",
    }

    try:
        reader = csv.DictReader(
            io.StringIO(csv_content)
        )

        if reader.fieldnames is None:
            raise ValueError(
                "CSV file is empty or has no header row."
            )

        fieldnames = {
            field.strip().lower()
            for field in reader.fieldnames
            if field is not None
        }

        missing_columns = sorted(
            required_columns - fieldnames
        )

        if missing_columns:
            raise ValueError(
                "Missing required CSV columns: "
                + ", ".join(missing_columns)
            )

        rows = list(reader)

    except csv.Error as exc:
        raise ValueError(
            f"Malformed CSV file: {exc}"
        ) from exc

    total = len(rows)
    created = 0
    skipped = 0
    failed = 0
    errors: list[dict] = []
    created_employees: list[Employee] = []

    seen_employee_ids: set[str] = set()
    seen_emails: set[str] = set()

    for row_number, raw_row in enumerate(rows, start=2):
        row = {
            (
                key.strip().lower()
                if key
                else ""
            ): (
                value.strip()
                if isinstance(value, str)
                else value
            )
            for key, value in raw_row.items()
        }

        employee_id = row.get("employee_id") or ""
        employee_name = row.get("employee_name") or ""
        email = row.get("email") or ""
        branch = row.get("branch") or ""
        department = row.get("department") or ""

        if not employee_id or not employee_name or not email:
            failed += 1
            errors.append(
                {
                    "row": row_number,
                    "error": (
                        "Missing employee_id, "
                        "employee_name, or email."
                    ),
                }
            )
            continue

        normalized_email = email.lower()

        if employee_id in seen_employee_ids:
            skipped += 1
            errors.append(
                {
                    "row": row_number,
                    "employee_id": employee_id,
                    "email": email,
                    "error": "Duplicate employee ID in CSV.",
                }
            )
            continue

        if normalized_email in seen_emails:
            skipped += 1
            errors.append(
                {
                    "row": row_number,
                    "employee_id": employee_id,
                    "email": email,
                    "error": "Duplicate email in CSV.",
                }
            )
            continue

        seen_employee_ids.add(employee_id)
        seen_emails.add(normalized_email)

        try:
            department_id = await _resolve_department(
                db,
                organization_id,
                department,
            )

            employee_data = EmployeeCreateRequest(
                employee_id=employee_id,
                name=employee_name,
                email=email,
                branch=branch or None,
                department_id=department_id,
            )

            employee = await create_employee(
                db,
                organization_id,
                employee_data,
            )

            created += 1
            created_employees.append(employee)

        except ValidationError as exc:
            failed += 1
            errors.append(
                {
                    "row": row_number,
                    "employee_id": employee_id,
                    "email": email,
                    "error": "Invalid employee data.",
                    "details": exc.errors(),
                }
            )

        except ValueError as exc:
            failed += 1
            errors.append(
                {
                    "row": row_number,
                    "employee_id": employee_id,
                    "email": email,
                    "error": str(exc),
                }
            )

    return {
        "total": total,
        "created": created,
        "skipped": skipped,
        "failed": failed,
        "errors": errors,
        "employees": created_employees,
    }