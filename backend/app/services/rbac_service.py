from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.permission import Permission
from app.db.models.role import Role
from app.db.models.role_permission import RolePermission


async def get_role_by_name(
    db: AsyncSession,
    role_name: str,
) -> Role | None:
    """Return a role by its unique name."""
    result = await db.execute(
        select(Role).where(Role.name == role_name)
    )
    return result.scalar_one_or_none()


async def get_permission_by_name(
    db: AsyncSession,
    permission_name: str,
) -> Permission | None:
    """Return a permission by its unique name."""
    result = await db.execute(
        select(Permission).where(Permission.name == permission_name)
    )
    return result.scalar_one_or_none()


async def role_has_permission(
    db: AsyncSession,
    role_id: UUID,
    permission_name: str,
) -> bool:
    """Return True when the role has the requested permission."""

    result = await db.execute(
        select(RolePermission.role_id)
        .join(
            Permission,
            Permission.id == RolePermission.permission_id,
        )
        .where(
            RolePermission.role_id == role_id,
            Permission.name == permission_name,
        )
    )

    return result.scalar_one_or_none() is not None