from dataclasses import dataclass
from datetime import datetime, UTC, timedelta
from enum import StrEnum
from typing import Callable
from uuid import UUID

from .suspensions import (
    SuspensionService,
    TemporarySuspension,
)


class WarningLevel(StrEnum):
    WARNING_1 = "WARNING_1"
    WARNING_2 = "WARNING_2"
    WARNING_3 = "WARNING_3"
    SUSPENSION = "SUSPENSION"


@dataclass(frozen=True)
class WarningPolicy:
    low_score_threshold: int
    warning_interval: timedelta = timedelta(hours=12)
    suspension_duration: timedelta = timedelta(hours=24)


@dataclass
class WarningState:
    subject_id: UUID
    organization_id: UUID
    warning_count: int = 0
    last_warning_at: datetime | None = None
    suspension_id: UUID | None = None


@dataclass(frozen=True)
class WarningResult:
    subject_id: UUID
    warning_level: WarningLevel | None
    warning_count: int
    suspended: bool
    suspension: TemporarySuspension | None
    occurred_at: datetime


class SecurityWarningService:
    def __init__(
        self,
        policy: WarningPolicy,
        suspension_service: SuspensionService,
        clock: Callable[[], datetime] | None = None,
    ):
        self.policy = policy
        self.suspension_service = suspension_service
        self.clock = clock or (lambda: datetime.now(UTC))
        self._states: dict[UUID, WarningState] = {}

    def _get_state(
        self,
        subject_id: UUID,
        organization_id: UUID,
    ) -> WarningState:
        state = self._states.get(subject_id)

        if state is None:
            state = WarningState(
                subject_id=subject_id,
                organization_id=organization_id,
            )
            self._states[subject_id] = state

        return state

    def evaluate(
        self,
        *,
        subject_id: UUID,
        organization_id: UUID,
        cyber_score: int,
    ) -> WarningResult:
        now = self.clock()

        if not 0 <= cyber_score <= 100:
            raise ValueError("Cyber score must be between 0 and 100")

        state = self._get_state(subject_id, organization_id)

        if cyber_score >= self.policy.low_score_threshold:
            state.warning_count = 0
            state.last_warning_at = None

            return WarningResult(
                subject_id=subject_id,
                warning_level=None,
                warning_count=0,
                suspended=False,
                suspension=None,
                occurred_at=now,
            )

        if (
            state.last_warning_at is not None
            and now - state.last_warning_at < self.policy.warning_interval
        ):
            suspension = None

            if state.suspension_id is not None:
                suspension = self.suspension_service.refresh_status(
                    state.suspension_id,
                    now=now,
                )

            return WarningResult(
                subject_id=subject_id,
                warning_level=None,
                warning_count=state.warning_count,
                suspended=(
                    suspension is not None
                    and suspension.status.value == "ACTIVE"
                ),
                suspension=suspension,
                occurred_at=now,
            )

        if state.warning_count < 3:
            state.warning_count += 1
            state.last_warning_at = now

            warning_level = WarningLevel(
                f"WARNING_{state.warning_count}"
            )

            return WarningResult(
                subject_id=subject_id,
                warning_level=warning_level,
                warning_count=state.warning_count,
                suspended=False,
                suspension=None,
                occurred_at=now,
            )

        if state.suspension_id is None:
            suspension = self.suspension_service.create(
                subject_id=subject_id,
                organization_id=organization_id,
                reason=(
                    "Cyber Score remained below the configured "
                    "security threshold."
                ),
                trigger="WARNING_3",
                duration=self.policy.suspension_duration,
                created_by="system",
                audit_info=(
                    "Automatic temporary suspension after "
                    "security warning sequence."
                ),
                now=now,
            )

            state.suspension_id = suspension.id

            return WarningResult(
                subject_id=subject_id,
                warning_level=WarningLevel.SUSPENSION,
                warning_count=state.warning_count,
                suspended=True,
                suspension=suspension,
                occurred_at=now,
            )

        suspension = self.suspension_service.refresh_status(
            state.suspension_id,
            now=now,
        )

        return WarningResult(
            subject_id=subject_id,
            warning_level=WarningLevel.SUSPENSION,
            warning_count=state.warning_count,
            suspended=suspension.status.value == "ACTIVE",
            suspension=suspension,
            occurred_at=now,
        )


def create_default_warning_service() -> SecurityWarningService:
    return SecurityWarningService(
        policy=WarningPolicy(
            low_score_threshold=40,
            warning_interval=timedelta(hours=12),
            suspension_duration=timedelta(hours=24),
        ),
        suspension_service=SuspensionService(),
    )


warning_service = create_default_warning_service()