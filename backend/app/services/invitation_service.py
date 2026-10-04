from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.employee import Employee
from app.db.models.invitation import Invitation, InvitationStatus


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def create_invitation(
    db: AsyncSession,
    *,
    organization_id: UUID,
    employee_id: UUID,
    invited_by: UUID,
    expires_in_hours: int = 72,
) -> tuple[Invitation, str]:
    employee = await db.scalar(
        select(Employee).where(
            Employee.id == employee_id,
            Employee.organization_id == organization_id,
        )
    )

    if employee is None:
        raise ValueError("Employee not found in organization")

    if employee.status != "ACTIVE":
        raise ValueError("Only active employees can be invited")

    existing = await db.scalar(
        select(Invitation).where(
            Invitation.employee_id == employee_id,
            Invitation.organization_id == organization_id,
            Invitation.status == InvitationStatus.PENDING,
        )
    )

    if existing is not None:
        raise ValueError("A pending invitation already exists")

    token = secrets.token_urlsafe(48)

    invitation = Invitation(
        organization_id=organization_id,
        employee_id=employee_id,
        token_hash=_hash_token(token),
        expires_at=datetime.now(timezone.utc)
        + timedelta(hours=expires_in_hours),
        status=InvitationStatus.PENDING,
        invited_by=invited_by,
    )

    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)

    return invitation, token


async def accept_invitation(
    db: AsyncSession,
    *,
    token: str,
    organization_id: UUID,
) -> Invitation:
    token_hash = _hash_token(token)

    invitation = await db.scalar(
        select(Invitation).where(
            Invitation.token_hash == token_hash,
            Invitation.organization_id == organization_id,
        )
    )

    if invitation is None:
        raise ValueError("Invalid invitation token")

    if invitation.status != InvitationStatus.PENDING:
        raise ValueError("Invitation is no longer valid")

    now = datetime.now(timezone.utc)

    if invitation.expires_at <= now:
        invitation.status = InvitationStatus.EXPIRED
        await db.commit()
        raise ValueError("Invitation has expired")

    invitation.status = InvitationStatus.ACCEPTED

    await db.commit()
    await db.refresh(invitation)

    return invitation


async def revoke_invitation(
    db: AsyncSession,
    *,
    organization_id: UUID,
    invitation_id: UUID,
) -> Invitation:
    invitation = await db.scalar(
        select(Invitation).where(
            Invitation.id == invitation_id,
            Invitation.organization_id == organization_id,
        )
    )

    if invitation is None:
        raise ValueError("Invitation not found")

    if invitation.status != InvitationStatus.PENDING:
        raise ValueError("Only pending invitations can be revoked")

    invitation.status = InvitationStatus.REVOKED

    await db.commit()
    await db.refresh(invitation)

    return invitation