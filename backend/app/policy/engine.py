from .contracts import (
    PolicyContext,
    PolicyDecision,
    PolicyEvaluation,
    PolicyInput,
    SecurityPolicy,
)


def evaluate_policy(
    context: PolicyContext | PolicyInput,
    policy: SecurityPolicy | None = None,
) -> PolicyEvaluation:
    configured_policy = policy or SecurityPolicy()

    if context.risk_score < 0 or context.risk_score > 100:
        raise ValueError("Risk score must be between 0 and 100")

    if context.confidence < 0 or context.confidence > 1:
        raise ValueError("Confidence must be between 0 and 1")

    if (
        context.risk_score >= configured_policy.minimum_risk_score
        and context.confidence >= configured_policy.minimum_confidence
    ):
        return PolicyEvaluation(
            decision=PolicyDecision.REQUIRE_ADMIN_REVIEW,
            reason=(
                "Risk score and confidence meet the configured "
                "security policy thresholds."
            ),
            policy_version=configured_policy.version,
            create_incident=configured_policy.create_incident,
            create_alert=configured_policy.create_alert,
        )

    return PolicyEvaluation(
        decision=PolicyDecision.ALLOW,
        reason="Event does not meet the configured security policy thresholds.",
        policy_version=configured_policy.version,
        create_incident=False,
        create_alert=False,
    )