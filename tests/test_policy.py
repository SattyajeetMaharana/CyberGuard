from app.policy.contracts import PolicyInput
from app.policy.engine import evaluate_policy


def test_policy_returns_decision():
    data = PolicyInput(
        risk_score=85,
        confidence=0.92,
        category="ATO"
    )

    decision = evaluate_policy(data)

    assert decision.action == "review"
    assert decision.requires_admin_review is True