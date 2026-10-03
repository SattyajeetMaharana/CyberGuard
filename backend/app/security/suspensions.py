from dataclasses import dataclass
from datetime import datetime, UTC, timedelta
from enum import StrEnum
from uuid import UUID, uuid4


class SuspensionStatus(StrEnum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


@dataclass
class TemporarySuspension:
    id: UUID
    subject_id: UUID
    organization_id: UUID
    reason: str
    trigger: str
    started_at: datetime
    expires_at: datetime
    status: SuspensionStatus
    created_by: str
    created_at: datetime
    revoked_at: datetime | None = None
    audit_info: str | None = None


class SuspensionService:
    def __init__(self):
        self._suspensions: dict[UUID, TemporarySuspension] = {}

    def create(
        self,
        *,
        subject_id: UUID,
        organization_id: UUID,
        reason: str,
        trigger: str,
        duration: timedelta,
        created_by: str = "system",
        audit_info: str | None = None,
        now: datetime | None = None,
    ) -> TemporarySuspension:
        now = now or datetime.now(UTC)

        suspension = TemporarySuspension(
            id=uuid4(),
            subject_id=subject_id,
            organization_id=organization_id,
            reason=reason,
            trigger=trigger,
            started_at=now,
            expires_at=now + duration,
            status=SuspensionStatus.ACTIVE,
            created_by=created_by,
            created_at=now,
            audit_info=audit_info,
        )

        self._suspensions[suspension.id] = suspension
        return suspension

    def get(self, suspension_id: UUID) -> TemporarySuspension | None:
        return self._suspensions.get(suspension_id)

    def refresh_status(
        self,
        suspension_id: UUID,
        *,
        now: datetime | None = None,
    ) -> TemporarySuspension:
        suspension = self._suspensions.get(suspension_id)

        if suspension is None:
            raise KeyError(f"Suspension {suspension_id} not found")

        now = now or datetime.now(UTC)

        if (
            suspension.status == SuspensionStatus.ACTIVE
            and now >= suspension.expires_at
        ):
            suspension.status = SuspensionStatus.EXPIRED

        return suspension

    def revoke(
        self,
        suspension_id: UUID,
        *,
        now: datetime | None = None,
    ) -> TemporarySuspension:
        suspension = self._suspensions.get(suspension_id)

        if suspension is None:
            raise KeyError(f"Suspension {suspension_id} not found")

        now = now or datetime.now(UTC)

        if suspension.status == SuspensionStatus.ACTIVE:
            suspension.status = SuspensionStatus.REVOKED
            suspension.revoked_at = now

        return suspension

    def is_active(
        self,
        subject_id: UUID,
        *,
        now: datetime | None = None,
    ) -> bool:
        now = now or datetime.now(UTC)

        for suspension in self._suspensions.values():
            if suspension.subject_id != subject_id:
                continue

            self.refresh_status(suspension.id, now=now)

            if suspension.status == SuspensionStatus.ACTIVE:
                return True

        return False

    def get_all(self) -> list[TemporarySuspension]:
        return list(self._suspensions.values())


suspension_service = SuspensionService()