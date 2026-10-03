from __future__ import annotations

import re

from .contracts import AssistantContext, AssistantResponse


_SECRET_PATTERNS = (
    r"-----BEGIN .* PRIVATE KEY-----",
    r"\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token)\s*[:=]\s*\S+",
    r"\bpassword\s*[:=]\s*\S+",
    r"\b(?:bearer|basic)\s+[A-Za-z0-9._~+/=-]{12,}",
)

_DESTRUCTIVE_PATTERNS = (
    r"\bdelete all\b",
    r"\bformat (?:the )?(?:disk|drive|system)\b",
    r"\bwipe (?:the )?(?:device|system|account)\b",
    r"\bdestroy\b",
    r"\bdisable all security\b",
)

_UNSUPPORTED_CERTAINTY = (
    "definitely",
    "certainly",
    "without a doubt",
    "100% confirmed",
    "guaranteed",
)


def _contains_pattern(text: str, patterns: tuple[str, ...]) -> bool:
    lowered = text.lower()

    return any(
        re.search(pattern, lowered, re.IGNORECASE)
        for pattern in patterns
    )


def validate_response(response: AssistantResponse) -> bool:
    """
    Backward-compatible boolean validator.
    """
    return validate_response_details(response)[0]


def validate_response_details(
    response: AssistantResponse,
    context: AssistantContext | None = None,
) -> tuple[bool, str]:

    message = response.message.strip()

    if not message:
        return False, "Assistant response is empty."

    if _contains_pattern(message, _SECRET_PATTERNS):
        return False, "Response contains potentially sensitive credentials."

    if _contains_pattern(message, _DESTRUCTIVE_PATTERNS):
        return False, "Response contains an unsafe destructive instruction."

    if _contains_pattern(message, _UNSUPPORTED_CERTAINTY):
        return False, "Response contains unsupported certainty."

    if context is not None:
        category = context.category.lower()

        if (
            category not in message.lower()
            and context.xai_summary
            and "evidence" not in message.lower()
        ):
            # This is intentionally not a hard failure.
            # The assistant may describe evidence without repeating
            # the category literally.
            pass

    return True, "valid"


def safe_fallback(
    context: AssistantContext,
    reason: str,
) -> AssistantResponse:

    return AssistantResponse(
        message=(
            f"The system identified a {context.risk_level.lower()}-risk "
            f"{context.category} event. "
            f"Available evidence: "
            f"{context.xai_summary or 'No additional explanation was provided.'} "
            f"Recommended next step: review the security recommendations "
            f"and follow the required approval process. "
            f"Assistant validation note: {reason}"
        ),
        evidence=context.indicators,
        requires_approval=bool(context.recommended_actions),
        safe=True,
        provider="validated-fallback",
    )
