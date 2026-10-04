from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.organization import Organization, OrganizationStatus
from app.db.models.organization_verification import (
    OrganizationVerification,
    VerificationStatus,
)


async def list_pending_organizations(
    db: AsyncSession,
) -> list[tuple[Organization, OrganizationVerification]]:
    result = await db.execute(
        select(Organization, OrganizationVerification)
        .join(
            OrganizationVerification,
            OrganizationVerification.organization_id == Organization.id,
        )
        .where(
            Organization.status.in_(
                [
                    OrganizationStatus.PENDING,
                    OrganizationStatus.UNDER_REVIEW,
                ]
            ),
            OrganizationVerification.status.in_(
                [
                    VerificationStatus.PENDING,
                    VerificationStatus.UNDER_REVIEW,
                ]
            ),
        )
        .order_by(Organization.created_at.asc())
    )

    return list(result.all())


async def get_organization_verification(
    db: AsyncSession,
    organization_id: UUID,
) -> tuple[Organization, OrganizationVerification] | None:
    result = await db.execute(
        select(Organization, OrganizationVerification)
        .join(
            OrganizationVerification,
            OrganizationVerification.organization_id == Organization.id,
        )
        .where(Organization.id == organization_id)
    )

    return result.one_or_none()


async def approve_organization(
    db: AsyncSession,
    organization_id: UUID,
    reviewed_by: UUID,
    review_notes: str | None = None,
) -> tuple[Organization, OrganizationVerification] | None:
    record = await get_organization_verification(
        db,
        organization_id,
    )

    if record is None:
        return None

    organization, verification = record

    organization.status = OrganizationStatus.VERIFIED
    verification.status = VerificationStatus.VERIFIED
    verification.reviewed_by = reviewed_by
    verification.review_notes = review_notes

    await db.commit()
    await db.refresh(organization)
    await db.refresh(verification)

    return organization, verification


async def reject_organization(
    db: AsyncSession,
    organization_id: UUID,
    reviewed_by: UUID,
    review_notes: str | None = None,
) -> tuple[Organization, OrganizationVerification] | None:
    record = await get_organization_verification(
        db,
        organization_id,
    )

    if record is None:
        return None

    organization, verification = record

    organization.status = OrganizationStatus.REJECTED
    verification.status = VerificationStatus.REJECTED
    verification.reviewed_by = reviewed_by
    verification.review_notes = review_notes

    await db.commit()
    await db.refresh(organization)
    await db.refresh(verification)

    return organization, verification


async def suspend_organization(
    db: AsyncSession,
    organization_id: UUID,
    reviewed_by: UUID,
    review_notes: str | None = None,
) -> tuple[Organization, OrganizationVerification] | None:
    record = await get_organization_verification(
        db,
        organization_id,
    )

    if record is None:
        return None

    organization, verification = record

    organization.status = OrganizationStatus.SUSPENDED
    verification.status = VerificationStatus.SUSPENDED
    verification.reviewed_by = reviewed_by
    verification.review_notes = review_notes

    await db.commit()
    await db.refresh(organization)
    await db.refresh(verification)

    return organization, verification