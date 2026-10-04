from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.employee import Employee
from app.db.models.security_context import SecurityContext
from app.db.models.security_context_membership import SecurityContextMembership


async def get_organization_context(
    db: AsyncSession,
    *,
    user_id: UUID,
    organization_id: UUID,
) -> SecurityContext | None:
    return await db.scalar(
        select(SecurityContext).where(
            SecurityContext.user_id == user_id,
            SecurityContext.organization_id == organization_id,
            SecurityContext.context_type == "ORGANIZATION",
            SecurityContext.is_active.is_(True),
        )
    )


async def create_organization_context(
    db: AsyncSession,
    *,
    user_id: UUID,
    organization_id: UUID,
) -> SecurityContext:
    existing = await get_organization_context(
        db,
        user_id=user_id,
        organization_id=organization_id,
    )

    if existing is not None:
        return existing

    context = SecurityContext(
        context_type="ORGANIZATION",
        user_id=user_id,
        organization_id=organization_id,
        is_active=True,
    )

    db.add(context)
    await db.commit()
    await db.refresh(context)

    return context


async def add_employee_membership(
    db: AsyncSession,
    *,
    context_id: UUID,
    organization_id: UUID,
    employee_id: UUID,
) -> SecurityContextMembership:
    employee = await db.scalar(
        select(Employee).where(
            Employee.id == employee_id,
            Employee.organization_id == organization_id,
        )
    )

    if employee is None:
        raise ValueError("Employee does not belong to organization")

    existing = await db.scalar(
        select(SecurityContextMembership).where(
            SecurityContextMembership.security_context_id == context_id,
            SecurityContextMembership.organization_id == organization_id,
            SecurityContextMembership.employee_id == employee_id,
            SecurityContextMembership.is_active.is_(True),
        )
    )

    if existing is not None:
        return existing

    membership = SecurityContextMembership(
        security_context_id=context_id,
        organization_id=organization_id,
        employee_id=employee_id,
        is_active=True,
    )

    db.add(membership)
    await db.commit()
    await db.refresh(membership)

    return membership


async def get_memberships(
    db: AsyncSession,
    *,
    context_id: UUID,
    organization_id: UUID,
) -> list[SecurityContextMembership]:
    result = await db.scalars(
        select(SecurityContextMembership)
        .where(
            SecurityContextMembership.security_context_id == context_id,
            SecurityContextMembership.organization_id == organization_id,
            SecurityContextMembership.is_active.is_(True),
        )
        .order_by(SecurityContextMembership.created_at)
    )

    return list(result.all())