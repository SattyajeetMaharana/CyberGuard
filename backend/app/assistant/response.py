from __future__ import annotations

from uuid import UUID

from .contracts import ApprovalRequest, AssistantContext

from app.orchestration.service import (
    ResponseAction as OrchestrationResponseAction,
    response_approval_service,
    audit_service,
)


def create_approval_request(
    *,
    incident_id: str,
    context: AssistantContext,
    action: str,
    reason: str,
) -> tuple[OrchestrationResponseAction, ApprovalRequest]:

    response = OrchestrationResponseAction(
        id=UUID(incident_id),
        category=context.category,
        actions=[action],
        target=incident_id,
        reason=reason,
    )

    # Submit to the EXISTING Phase 3 approval workflow.
    response_approval_service.submit_for_review(response)

    request = ApprovalRequest(
        response_id=str(response.id),
        incident_id=context.incident_id,
        action=action,
        reason=reason,
        state=response.state.value,
    )

    audit_service.record(
        actor="assistant",
        action="RESPONSE_APPROVAL_REQUESTED",
        target=context.incident_id,
        reason=reason,
        outcome=response.state.value,
    )

    return response, request


def approve_response(
    response: OrchestrationResponseAction,
    *,
    approver: str,
) -> OrchestrationResponseAction:

    response_approval_service.approve(response)

    audit_service.record(
        actor=approver,
        action="RESPONSE_APPROVED",
        target=str(response.id),
        reason=response.reason or "Assistant recommendation approved.",
        outcome=response.state.value,
    )

    return response


def execute_response(
    response: OrchestrationResponseAction,
    *,
    executor: str,
) -> OrchestrationResponseAction:

    response_approval_service.execute(response)

    audit_service.record(
        actor=executor,
        action="RESPONSE_EXECUTED",
        target=str(response.id),
        reason=response.reason or "Approved response executed.",
        outcome=response.state.value,
    )

    return response
