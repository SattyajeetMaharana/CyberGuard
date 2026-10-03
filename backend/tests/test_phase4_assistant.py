from uuid import uuid4

import pytest

from app.assistant.context import build_context
from app.assistant.contracts import AssistantResponse
from app.assistant.service import (
    AssistantService,
    LocalLLMProvider,
)
from app.assistant.validator import (
    validate_response,
    validate_response_details,
)
from app.assistant.conversations import (
    AssistantConversationService,
)
from app.assistant.playbooks import (
    load_account_takeover_playbook,
)
from app.assistant.response import (
    approve_response,
    create_approval_request,
    execute_response,
)


def test_context_builder_creates_risk_level():
    context = build_context(
        incident_id="inc-1",
        category="phishing",
        risk_score=75,
        confidence=0.91,
        explanation="Suspicious sender and domain mismatch.",
        indicators=["domain_mismatch", "urgent_request"],
        incident_status="CONFIRMED",
        recommended_actions=["notify_admin"],
        security_context={
            "source": "email",
            "password": "DO_NOT_STORE",
        },
    )

    assert context.risk_level == "HIGH"
    assert context.confidence == 0.91
    assert "domain_mismatch" in context.indicators
    assert context.security_context["password"] == "[REDACTED]"


def test_context_rejects_invalid_values():
    with pytest.raises(ValueError):
        build_context(
            incident_id="inc-1",
            category="phishing",
            risk_score=101,
            confidence=0.9,
        )

    with pytest.raises(ValueError):
        build_context(
            incident_id="inc-1",
            category="phishing",
            risk_score=50,
            confidence=1.5,
        )


def test_fallback_works_without_model():
    context = build_context(
        incident_id="inc-2",
        category="malicious_url",
        risk_score=82,
        confidence=0.88,
        explanation="URL contains suspicious characteristics.",
    )

    service = AssistantService(
        local_provider=LocalLLMProvider(),
    )

    response = service.respond(context)

    assert response.safe is True
    assert response.provider == "deterministic-fallback"
    assert "suspicious URL" in response.message


def test_local_model_is_used_when_available():
    def fake_model(context):
        return (
            f"Evidence-based guidance for {context.category}. "
            "Review the available evidence."
        )

    context = build_context(
        incident_id="inc-3",
        category="phishing",
        risk_score=55,
        confidence=0.80,
        explanation="Suspicious sender.",
    )

    service = AssistantService(
        local_provider=LocalLLMProvider(fake_model),
    )

    response = service.respond(context)

    assert response.provider == "local-llm"


def test_missing_model_falls_back():
    context = build_context(
        incident_id="inc-4",
        category="impersonation",
        risk_score=65,
        confidence=0.75,
        explanation="Identity indicators require verification.",
    )

    service = AssistantService(
        local_provider=LocalLLMProvider(None),
    )

    response = service.respond(context)

    assert response.safe
    assert response.provider == "deterministic-fallback"


def test_unsafe_output_is_rejected():
    response = AssistantResponse(
        message="Definitely delete all account data immediately.",
    )

    assert validate_response(response) is False


def test_secret_output_is_rejected():
    response = AssistantResponse(
        message="The password=SuperSecret123 should be used.",
    )

    assert validate_response(response) is False


def test_unsupported_certainty_is_rejected():
    response = AssistantResponse(
        message="This is definitely a confirmed attack.",
    )

    assert validate_response(response) is False


def test_valid_output_is_accepted():
    response = AssistantResponse(
        message="The evidence indicates that review is appropriate.",
    )

    assert validate_response(response) is True


def test_conversation_creation_and_messages():
    service = AssistantConversationService()

    conversation = service.create(
        threat_context="phishing",
    )

    message = service.add_message(
        conversation_id=conversation.id,
        role="assistant",
        content="Review the suspicious message.",
    )

    assert message.conversation_id == conversation.id
    assert len(service.messages(conversation.id)) == 1


def test_account_takeover_playbook_loads():
    playbook = load_account_takeover_playbook()

    assert playbook.name == "account_takeover_response"
    assert playbook.threat_category == "account_takeover"
    assert len(playbook.actions) == 4

    assert all(
        action.approval_required
        for action in playbook.actions
    )


def test_response_requires_existing_approval_workflow():
    incident_id = str(uuid4())

    context = build_context(
        incident_id=incident_id,
        category="account_takeover",
        risk_score=90,
        confidence=0.95,
        explanation="Suspicious login activity.",
        recommended_actions=["revoke_session"],
    )

    response, request = create_approval_request(
        incident_id=incident_id,
        context=context,
        action="revoke_session",
        reason="Suspicious account activity requires review.",
    )

    assert request.state == "ADMIN_REVIEW"
    assert response.state.value == "ADMIN_REVIEW"

    approve_response(
        response,
        approver="security-admin",
    )

    assert response.state.value == "APPROVED"

    execute_response(
        response,
        executor="security-system",
    )

    assert response.state.value == "EXECUTED"


def test_response_cannot_skip_approval():
    incident_id = str(uuid4())

    context = build_context(
        incident_id=incident_id,
        category="account_takeover",
        risk_score=90,
        confidence=0.95,
    )

    response, _ = create_approval_request(
        incident_id=incident_id,
        context=context,
        action="suspend_device",
        reason="Suspicious device activity.",
    )

    with pytest.raises(ValueError):
        execute_response(
            response,
            executor="security-system",
        )


def test_threat_specific_categories():
    categories = (
        "phishing",
        "malicious_url",
        "impersonation",
        "deepfake",
        "account_takeover",
    )

    service = AssistantService()

    for category in categories:
        context = build_context(
            incident_id=f"inc-{category}",
            category=category,
            risk_score=70,
            confidence=0.80,
            explanation=f"Evidence for {category}.",
        )

        response = service.respond(context)

        assert response.safe
        assert response.message


def test_malformed_detection_values_are_rejected():
    with pytest.raises(ValueError):
        build_context(
            incident_id="bad",
            category="phishing",
            risk_score=-1,
            confidence=0.5,
        )

def test_response_approval_uses_separate_response_id():
    from app.assistant.response import create_approval_request

    _, request = create_approval_request(
        incident_id="INC-2026-001",
        category="account_takeover",
        action="revoke_session",
        reason="Suspicious session detected",
    )

    assert request.incident_id == "INC-2026-001"
    assert request.response_id != request.incident_id


def test_conversation_redacts_password():
    from app.assistant.conversations import AssistantConversationService

    service = AssistantConversationService()

    conversation = service.create_conversation(
        "Account takeover investigation"
    )

    message = service.add_message(
        conversation.id,
        "user",
        "password=SuperSecret123",
    )

    assert "SuperSecret123" not in message.content
    assert "[REDACTED]" in message.content


def test_conversation_redacts_api_key():
    from app.assistant.conversations import AssistantConversationService

    service = AssistantConversationService()

    conversation = service.create_conversation(
        "Phishing investigation"
    )

    message = service.add_message(
        conversation.id,
        "user",
        "api_key=abc123",
    )

    assert "abc123" not in message.content
    assert "[REDACTED]" in message.content


def test_invalid_conversation_role_is_rejected():
    from app.assistant.conversations import AssistantConversationService

    service = AssistantConversationService()

    conversation = service.create_conversation(
        "Phishing investigation"
    )

    try:
        service.add_message(
            conversation.id,
            "attacker",
            "test",
        )
        assert False, "Invalid role should have raised ValueError"
    except ValueError:
        pass
