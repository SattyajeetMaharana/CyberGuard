from __future__ import annotations

from uuid import UUID, uuid4

from app.assistant.contracts import ApprovalRequest, AssistantContext
from app.assistant.notifications import notify_response_approval_required
from app.orchestration.service import (
    ResponseAction,
    ResponseApprovalService,
    ResponseState,
    audit_service,
)


response_approval_service = ResponseApprovalService()


def create_approval_request(
    incident_id: str,
    context: AssistantContext | None = None,
    action: str = "",
    reason: str = "",
    category: str | None = None,
    target: str | None = None,
) -> tuple[ResponseAction, ApprovalRequest]:
    if context is not None:
        resolved_category = context.category
    elif category is not None:
        resolved_category = category
    else:
        resolved_category = "assistant_response"

    response = ResponseAction(
        id=uuid4(),
        category=resolved_category,
        actions=[action],
        target=target,
        reason=reason,
    )

    # Recommendation -> Approval Required
    response_approval_service.submit_for_review(response)

    notify_response_approval_required(
        incident_id=incident_id,
        category=resolved_category,
        action=action,
        reason=reason,
    )

    audit_service.record(
        actor="assistant",
        action="RESPONSE_APPROVAL_REQUESTED",
        target=incident_id,
        reason=reason,
        outcome="APPROVAL_REQUIRED",
    )

    request = ApprovalRequest(
        response_id=str(response.id),
        incident_id=incident_id,
        action=action,
        reason=reason,
        state=response.state.value,
    )

    return response, request


def approve_response(
    response: ResponseAction,
    approver: str = "authorized_user",
    reason: str = "Approved by authorized user",
) -> str:
    """
    Move an existing response from ADMIN_REVIEW to APPROVED.

    The existing ResponseAction object is intentionally used so the
    approval workflow cannot be bypassed by creating a new response.
    """
    if response.state != ResponseState.ADMIN_REVIEW:
        raise ValueError(
            f"Response must be in ADMIN_REVIEW before approval; "
            f"current state is {response.state.value}"
        )

    response_approval_service.approve(response)

    audit_service.record(
        actor=approver,
        action="RESPONSE_APPROVED",
        target=str(response.id),
        reason=reason,
        outcome="APPROVED",
    )

    return response.state.value


def execute_response(
    response: ResponseAction,
    executor: str = "response_executor",
    reason: str = "Approved response executed",
) -> str:
    """
    Execute an existing response only after it has been approved.

    Direct execution of a recommended/admin-review response is rejected.
    """
    if response.state != ResponseState.APPROVED:
        raise ValueError(
            f"Response must be APPROVED before execution; "
            f"current state is {response.state.value}"
        )

    response_approval_service.execute(response)

    audit_service.record(
        actor=executor,
        action="RESPONSE_EXECUTED",
        target=str(response.id),
        reason=reason,
        outcome="EXECUTED",
    )

    audit_service.record(
        actor=executor,
        action="RESPONSE_OUTCOME",
        target=str(response.id),
        reason=reason,
        outcome="SUCCESS",
    )

    return response.state.value
