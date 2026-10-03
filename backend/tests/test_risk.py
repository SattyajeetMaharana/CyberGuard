import pytest

from app.risk.contracts import RiskLevel
from app.risk.engine import classify_risk


@pytest.mark.parametrize(
    "score, expected",
    [
        (0, RiskLevel.SAFE),
        (19, RiskLevel.SAFE),
        (20, RiskLevel.LOW),
        (39, RiskLevel.LOW),
        (40, RiskLevel.MEDIUM),
        (59, RiskLevel.MEDIUM),
        (60, RiskLevel.HIGH),
        (79, RiskLevel.HIGH),
        (80, RiskLevel.CRITICAL),
        (100, RiskLevel.CRITICAL),
    ],
)
def test_risk_boundaries(score, expected):
    assert classify_risk(score) == expected


@pytest.mark.parametrize("score", [-1, 101])
def test_invalid_risk_score(score):
    with pytest.raises(ValueError):
        classify_risk(score)