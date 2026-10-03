from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4

from app.security.suspensions import (
    SuspensionService,
    TemporarySuspension,
)


class VoteChoice(StrEnum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"


class ReportStatus(StrEnum):
    OPEN = "OPEN"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class AdminReport:
    id: UUID
    organization_id: UUID
    reporter_id: UUID
    target_id: UUID
    reason: str


@dataclass(frozen=True)
class AdminVote:
    admin_id: UUID
    choice: VoteChoice


@dataclass
class SecurityReview:
    report: AdminReport
    status: ReportStatus
    votes: dict[UUID, AdminVote]


class AdminSecurityWorkflow:
    def __init__(
        self,
        suspension_service: SuspensionService,
    ):
        self.suspension_service = suspension_service
        self._reviews: dict[UUID, SecurityReview] = {}

    def create_report(
        self,
        *,
        organization_id: UUID,
        reporter_id: UUID,
        target_id: UUID,
        reason: str,
    ) -> SecurityReview:
        if reporter_id == target_id:
            raise ValueError("An admin cannot report themselves as the target.")

        report = AdminReport(
            id=uuid4(),
            organization_id=organization_id,
            reporter_id=reporter_id,
            target_id=target_id,
            reason=reason,
        )

        review = SecurityReview(
            report=report,
            status=ReportStatus.OPEN,
            votes={},
        )

        self._reviews[report.id] = review
        return review

    def get_review(self, report_id: UUID) -> SecurityReview | None:
        return self._reviews.get(report_id)

    def cast_vote(
        self,
        report_id: UUID,
        *,
        admin_id: UUID,
        choice: VoteChoice,
    ) -> SecurityReview:
        review = self._reviews.get(report_id)

        if review is None:
            raise KeyError(f"Security review {report_id} not found")

        if review.status != ReportStatus.OPEN:
            raise ValueError("This security review is already decided.")

        if admin_id == review.report.target_id:
            raise ValueError("The target cannot vote on their own report.")

        if admin_id in review.votes:
            raise ValueError("An admin can vote only once.")

        review.votes[admin_id] = AdminVote(
            admin_id=admin_id,
            choice=choice,
        )

        return review

    def decide(
        self,
        report_id: UUID,
        *,
        eligible_admin_ids: set[UUID],
    ) -> ReportStatus:
        review = self._reviews.get(report_id)

        if review is None:
            raise KeyError(f"Security review {report_id} not found")

        if review.status != ReportStatus.OPEN:
            return review.status

        eligible_voters = (
            eligible_admin_ids - {review.report.target_id}
        )

        votes = [
            vote
            for admin_id, vote in review.votes.items()
            if admin_id in eligible_voters
        ]

        if not votes:
            raise ValueError("No eligible votes have been cast.")

        approvals = sum(
            vote.choice == VoteChoice.APPROVE
            for vote in votes
        )

        rejections = sum(
            vote.choice == VoteChoice.REJECT
            for vote in votes
        )

        if approvals > rejections:
            review.status = ReportStatus.APPROVED
        else:
            review.status = ReportStatus.REJECTED

        return review.status

    def apply_decision(
        self,
        report_id: UUID,
        *,
        duration,
        created_by: str = "admin_workflow",
    ) -> TemporarySuspension | None:
        review = self._reviews.get(report_id)

        if review is None:
            raise KeyError(f"Security review {report_id} not found")

        if review.status != ReportStatus.APPROVED:
            return None

        return self.suspension_service.create(
            subject_id=review.report.target_id,
            organization_id=review.report.organization_id,
            reason=review.report.reason,
            trigger="ADMIN_MAJORITY_APPROVAL",
            duration=duration,
            created_by=created_by,
            audit_info=(
                f"Approved through admin security review "
                f"{review.report.id}."
            ),
        )