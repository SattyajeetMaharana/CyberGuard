from __future__ import annotations

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.models.credential import Credential
from app.db.models.organization import Organization, OrganizationStatus
from app.db.models.organization_verification import (
    OrganizationVerification,
    VerificationStatus,
)
from app.db.models.role import Role
from app.db.models.security_context import SecurityContext
from app.db.models.user import User


def generate_organization_web_id() -> str:
    """Generate a unique public-facing organization web ID."""
    return f"ORG-{uuid4().hex[:12].upper()}"


async def register_organization(
    db: AsyncSession,
    *,
    organization_email: str,
    password: str,
    organization_name: str,
    organization_identifier: str,
    proof_type: str | None = None,
    proof_reference: str | None = None,
) -> Organization:
    """
    Register a new organization and its initial organization user.

    New organizations always start in PENDING status and are never
    automatically verified.
    """

    existing_org_email = await db.execute(
        select(Organization).where(
            Organization.organization_email == organization_email
        )
    )

    if existing_org_email.scalar_one_or_none() is not None:
        raise ValueError("Organization email already registered")

    existing_identifier = await db.execute(
        select(Organization).where(
            Organization.organization_identifier == organization_identifier
        )
    )

    if existing_identifier.scalar_one_or_none() is not None:
        raise ValueError("Organization identifier already registered")

    existing_user = await db.execute(
        select(User).where(User.email == organization_email)
    )

    if existing_user.scalar_one_or_none() is not None:
        raise ValueError("Email already registered")

    role_result = await db.execute(
        select(Role).where(Role.name == "ORGANIZATION_ADMIN")
    )
    organization_admin_role = role_result.scalar_one_or_none()

    if organization_admin_role is None:
        raise RuntimeError(
            "ORGANIZATION_ADMIN role is not configured"
        )

    organization = Organization(
        name=organization_name,
        organization_email=organization_email,
        organization_identifier=organization_identifier,
        web_id=generate_organization_web_id(),
        status=OrganizationStatus.PENDING,
    )

    db.add(organization)
    await db.flush()

    user = User(
        email=organization_email,
        full_name=organization_name,
        role_id=organization_admin_role.id,
        is_active=True,
        is_verified=False,
    )

    db.add(user)
    await db.flush()

    credential = Credential(
        user_id=user.id,
        password_hash=hash_password(password),
        is_active=True,
    )

    db.add(credential)

    security_context = SecurityContext(
        context_type="ORGANIZATION",
        user_id=user.id,
        organization_id=organization.id,
        is_active=True,
    )

    db.add(security_context)

    verification = OrganizationVerification(
        organization_id=organization.id,
        proof_type=proof_type,
        proof_reference=proof_reference,
        status=VerificationStatus.PENDING,
    )

    db.add(verification)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise ValueError(
            "Organization registration conflicts with existing data"
        ) from exc

    await db.refresh(organization)

    return organization