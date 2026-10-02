import pytest

from ml.common.risk import RiskLevel, risk_level_from_score


def test_risk_boundaries():
    assert risk_level_from_score(0) == RiskLevel.SAFE
    assert risk_level_from_score(19) == RiskLevel.SAFE
    assert risk_level_from_score(20) == RiskLevel.LOW
    assert risk_level_from_score(39) == RiskLevel.LOW
    assert risk_level_from_score(40) == RiskLevel.MEDIUM
    assert risk_level_from_score(59) == RiskLevel.MEDIUM
    assert risk_level_from_score(60) == RiskLevel.HIGH
    assert risk_level_from_score(79) == RiskLevel.HIGH
    assert risk_level_from_score(80) == RiskLevel.CRITICAL
    assert risk_level_from_score(100) == RiskLevel.CRITICAL


def test_invalid_risk_score():
    with pytest.raises(ValueError):
        risk_level_from_score(-1)

    with pytest.raises(ValueError):
        risk_level_from_score(101)
