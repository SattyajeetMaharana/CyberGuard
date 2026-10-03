"""seed initial rbac roles and permissions

Revision ID: c279cc776780
Revises: 08c2abbe138c
Create Date: 2026-10-03 16:30:23.502225

"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c279cc776780"
down_revision: Union[str, Sequence[str], None] = "08c2abbe138c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ROLES = {
    "PERSONAL_USER": "Personal user",
    "ORGANIZATION_EMPLOYEE": "Organization employee",
    "ORGANIZATION_ADMIN": "Organization administrator",
    "SUPER_ADMIN": "Super administrator",
}

PERMISSIONS = {
    "users:read": "Read user information",
    "users:write": "Create and update user information",
    "users:delete": "Delete or deactivate users",
    "security:read": "Read security information",
    "security:analyze": "Submit security analysis requests",
    "security:manage": "Manage security configuration",
}


def upgrade() -> None:
    connection = op.get_bind()

    role_ids: dict[str, str] = {}
    permission_ids: dict[str, str] = {}

    # Create roles.
    for role_name, description in ROLES.items():
        role_id = str(uuid4())

        connection.execute(
            sa.text(
                """
                INSERT INTO roles (id, name, description)
                VALUES (:id, :name, :description)
                """
            ),
            {
                "id": role_id,
                "name": role_name,
                "description": description,
            },
        )

        role_ids[role_name] = role_id

    # Create permissions.
    for permission_name, description in PERMISSIONS.items():
        permission_id = str(uuid4())

        connection.execute(
            sa.text(
                """
                INSERT INTO permissions (id, name, description)
                VALUES (:id, :name, :description)
                """
            ),
            {
                "id": permission_id,
                "name": permission_name,
                "description": description,
            },
        )

        permission_ids[permission_name] = permission_id

    # Personal users.
    personal_permissions = [
        "users:read",
        "security:read",
        "security:analyze",
    ]

    # Organization employees.
    employee_permissions = [
        "users:read",
        "security:read",
        "security:analyze",
    ]

    # Organization administrators.
    organization_admin_permissions = [
        "users:read",
        "users:write",
        "users:delete",
        "security:read",
        "security:analyze",
        "security:manage",
    ]

    # Super administrators.
    super_admin_permissions = list(PERMISSIONS.keys())

    role_permissions = {
        "PERSONAL_USER": personal_permissions,
        "ORGANIZATION_EMPLOYEE": employee_permissions,
        "ORGANIZATION_ADMIN": organization_admin_permissions,
        "SUPER_ADMIN": super_admin_permissions,
    }

    for role_name, permission_names in role_permissions.items():
        for permission_name in permission_names:
            connection.execute(
                sa.text(
                    """
                    INSERT INTO role_permissions (role_id, permission_id)
                    VALUES (:role_id, :permission_id)
                    """
                ),
                {
                    "role_id": role_ids[role_name],
                    "permission_id": permission_ids[permission_name],
                },
            )


def downgrade() -> None:
    connection = op.get_bind()

    permission_names = list(PERMISSIONS.keys())
    role_names = list(ROLES.keys())

    permission_ids = connection.execute(
        sa.text(
            """
            SELECT id
            FROM permissions
            WHERE name = ANY(:names)
            """
        ),
        {"names": permission_names},
    ).scalars().all()

    if permission_ids:
        connection.execute(
            sa.text(
                """
                DELETE FROM role_permissions
                WHERE permission_id = ANY(:permission_ids)
                """
            ),
            {"permission_ids": permission_ids},
        )

    connection.execute(
        sa.text(
            """
            DELETE FROM permissions
            WHERE name = ANY(:names)
            """
        ),
        {"names": permission_names},
    )

    connection.execute(
        sa.text(
            """
            DELETE FROM roles
            WHERE name = ANY(:names)
            """
        ),
        {"names": role_names},
    )