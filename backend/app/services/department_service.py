from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.department import Department


async def create_department(
    db: AsyncSession,
    *,
    organization_id: UUID,
    name: str,
    code: str,
) -> Department:
    existing = await db.execute(
        select(Department).where(
            Department.organization_id == organization_id,
            Department.code == code,
        )
    )

    if existing.scalar_one_or_none() is not None:
        raise ValueError(
            "Department code already exists in this organization"
        )

    department = Department(
        organization_id=organization_id,
        name=name,
        code=code,
        is_active=True,
    )

    db.add(department)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ValueError(
            "Department code already exists in this organization"
        ) from exc

    await db.refresh(department)

    return department


async def list_departments(
    db: AsyncSession,
    *,
    organization_id: UUID,
) -> list[Department]:
    result = await db.execute(
        select(Department)
        .where(
            Department.organization_id == organization_id,
            Department.is_active.is_(True),
        )
        .order_by(Department.name.asc())
    )

    return list(result.scalars().all())


async def get_department(
    db: AsyncSession,
    *,
    organization_id: UUID,
    department_id: UUID,
) -> Department | None:
    result = await db.execute(
        select(Department).where(
            Department.id == department_id,
            Department.organization_id == organization_id,
        )
    )

    return result.scalar_one_or_none()


async def update_department(
    db: AsyncSession,
    *,
    organization_id: UUID,
    department_id: UUID,
    name: str | None = None,
    code: str | None = None,
    is_active: bool | None = None,
) -> Department | None:
    department = await get_department(
        db,
        organization_id=organization_id,
        department_id=department_id,
    )

    if department is None:
        return None

    if code is not None and code != department.code:
        existing = await db.execute(
            select(Department).where(
                Department.organization_id == organization_id,
                Department.code == code,
                Department.id != department_id,
            )
        )

        if existing.scalar_one_or_none() is not None:
            raise ValueError(
                "Department code already exists in this organization"
            )

        department.code = code

    if name is not None:
        department.name = name

    if is_active is not None:
        department.is_active = is_active

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ValueError(
            "Department code already exists in this organization"
        ) from exc

    await db.refresh(department)

    return department


async def delete_department(
    db: AsyncSession,
    *,
    organization_id: UUID,
    department_id: UUID,
) -> Department | None:
    department = await get_department(
        db,
        organization_id=organization_id,
        department_id=department_id,
    )

    if department is None:
        return None

    department.is_active = False

    await db.commit()
    await db.refresh(department)

    return department