from .contracts import (
    ResponseAction,
    ResponseRecommendation,
)


def recommend_response(
    *args,
    risk_level: str | None = None,
    category: str | None = None,
) -> list[ResponseRecommendation] | ResponseRecommendation:

    # Backward-compatible API:
    # recommend_response(action, reason)
    if len(args) == 2:
        action, reason = args

        return ResponseRecommendation(
            action=action,
            reason=reason,
            requires_approval=action == ResponseAction.NOTIFY_ADMIN,
        )

    recommendations: list[ResponseRecommendation] = []

    if category == "phishing_url":
        recommendations.extend(
            [
                ResponseRecommendation(
                    action=ResponseAction.DO_NOT_OPEN_URL,
                    reason="Do not open the suspicious URL.",
                    requires_approval=False,
                ),
                ResponseRecommendation(
                    action=ResponseAction.VERIFY_DOMAIN,
                    reason="Verify the domain before interacting with the message.",
                    requires_approval=False,
                ),
                ResponseRecommendation(
                    action=ResponseAction.REPORT_MESSAGE,
                    reason="Report the suspicious message to the security team.",
                    requires_approval=False,
                ),
                ResponseRecommendation(
                    action=ResponseAction.REMOVE_SUSPICIOUS_CONTENT,
                    reason="Remove suspicious content after review.",
                    requires_approval=True,
                ),
                ResponseRecommendation(
                    action=ResponseAction.NOTIFY_ADMIN,
                    reason="A potentially malicious URL was detected.",
                    requires_approval=True,
                ),
            ]
        )

    elif risk_level in {"HIGH", "CRITICAL"}:
        recommendations.append(
            ResponseRecommendation(
                action=ResponseAction.NOTIFY_ADMIN,
                reason="High-risk security event detected.",
                requires_approval=True,
            )
        )

    return recommendations