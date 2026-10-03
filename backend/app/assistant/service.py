from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Protocol

from .contracts import AssistantContext, AssistantResponse
from .validator import (
    safe_fallback,
    validate_response_details,
)


class AssistantProvider(Protocol):
    name: str

    def generate(
        self,
        context: AssistantContext,
    ) -> AssistantResponse:
        ...


class TemplateFallbackProvider:
    """
    Deterministic provider.

    This provider requires no model, network connection,
    API key, or external service.
    """

    name = "deterministic-fallback"

    _guidance = {
        "phishing": (
            "Do not open links or provide credentials. "
            "Verify the sender and domain through a trusted channel."
        ),
        "phishing_url": (
            "Do not open the suspicious URL. "
            "Verify the domain independently before interacting with it."
        ),
        "malicious_url": (
            "Do not open the suspicious URL. "
            "Verify the destination through a trusted source."
        ),
        "impersonation": (
            "Verify the identity through an independent trusted channel "
            "before sharing information or approving requests."
        ),
        "deepfake": (
            "Treat the media as unverified until independently confirmed. "
            "Use another trusted communication channel to verify the person."
        ),
        "account_takeover": (
            "Review active sessions and account activity. "
            "Use the approved account-security response process."
        ),
    }

    def generate(
        self,
        context: AssistantContext,
    ) -> AssistantResponse:

        category = context.category.lower()

        guidance = self._guidance.get(
            category,
            "Review the available evidence and follow the organization's security response process.",
        )

        evidence = context.xai_summary or (
            "No additional XAI explanation was supplied."
        )

        actions = ""

        if context.recommended_actions:
            actions = (
                " Recommended actions: "
                + ", ".join(context.recommended_actions)
                + "."
            )

        message = (
            f"Risk level: {context.risk_level}. "
            f"Risk score: {context.risk_score:.0f}/100. "
            f"Confidence: {context.confidence:.0%}. "
            f"Evidence: {evidence} "
            f"{guidance}"
            f"{actions}"
        )

        return AssistantResponse(
            message=message,
            evidence=context.indicators,
            requires_approval=bool(context.recommended_actions),
            safe=True,
            provider=self.name,
        )


class LocalLLMProvider:
    """
    Adapter for a locally hosted LLM.

    The backend does not depend on a particular model runtime.
    A callable can be supplied later by the ML team.

    If the callable fails or is unavailable, AssistantService
    automatically falls back to TemplateFallbackProvider.
    """

    name = "local-llm"

    def __init__(
        self,
        generator: Callable[[AssistantContext], str] | None = None,
    ):
        self._generator = generator

    @property
    def available(self) -> bool:
        return self._generator is not None

    def generate(
        self,
        context: AssistantContext,
    ) -> AssistantResponse:

        if self._generator is None:
            raise RuntimeError("Local LLM is unavailable.")

        message = self._generator(context)

        return AssistantResponse(
            message=str(message),
            evidence=context.indicators,
            requires_approval=bool(context.recommended_actions),
            safe=True,
            provider=self.name,
        )


class AssistantService:
    def __init__(
        self,
        *,
        local_provider: LocalLLMProvider | None = None,
        fallback_provider: AssistantProvider | None = None,
    ):
        self.local_provider = local_provider or LocalLLMProvider()
        self.fallback_provider = (
            fallback_provider or TemplateFallbackProvider()
        )

    def respond(
        self,
        context: AssistantContext,
    ) -> AssistantResponse:

        response: AssistantResponse

        if self.local_provider.available:
            try:
                response = self.local_provider.generate(context)

                valid, reason = validate_response_details(
                    response,
                    context,
                )

                if valid:
                    return response

                return safe_fallback(context, reason)

            except Exception:
                return safe_fallback(
                    context,
                    "Local model was unavailable or failed validation.",
                )

        response = self.fallback_provider.generate(context)

        valid, reason = validate_response_details(
            response,
            context,
        )

        if valid:
            return response

        return safe_fallback(context, reason)


assistant_service = AssistantService()
