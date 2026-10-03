import pytest

from ml.detectors.impersonation_detector import ImpersonationDetector


BENIGN_FEATURES = {
    "urgency_level": 1,
    "requests_wire_transfer": 0,
    "requests_gift_cards": 0,
    "requests_sensitive_data": 0,
    "dkim_pass": 1,
    "spf_pass": 1,
    "dmarc_pass": 1,
    "reply_to_mismatch": 0,
    "is_end_of_month": 0,
    "is_friday": 0,
    "sent_outside_hours": 0,
    "requested_amount_usd": 0,
    "auth_failure": 0,
    "partial_auth": 0,
    "full_auth_bypass": 0,
    "payroll_timing": 0,
    "weekend_timing": 0,
    "after_hours": 0,
}


IMPERSONATION_FEATURES = {
    "urgency_level": 5,
    "requests_wire_transfer": 1,
    "requests_gift_cards": 0,
    "requests_sensitive_data": 1,
    "dkim_pass": 0,
    "spf_pass": 0,
    "dmarc_pass": 0,
    "reply_to_mismatch": 1,
    "is_end_of_month": 0,
    "is_friday": 0,
    "sent_outside_hours": 1,
    "requested_amount_usd": 250000,
    "auth_failure": 1,
    "partial_auth": 0,
    "full_auth_bypass": 1,
    "payroll_timing": 0,
    "weekend_timing": 0,
    "after_hours": 1,
}


@pytest.fixture
def detector():
    return ImpersonationDetector()


def test_benign_detection(detector):
    event = {
        "category": "impersonation",
        "features": BENIGN_FEATURES,
    }

    result = detector.analyze(event)

    assert result.category == "impersonation"
    assert result.prediction == "benign"
    assert result.risk_level == "SAFE"
    assert 0 <= result.risk_score < 20
    assert 0 <= result.confidence <= 1
    assert result.model_version == "impersonation-xgboost-v1"
    assert result.indicators
    assert result.explanation
    assert result.recommended_actions


def test_impersonation_detection(detector):
    event = {
        "category": "impersonation",
        "features": IMPERSONATION_FEATURES,
    }

    result = detector.analyze(event)

    assert result.category == "impersonation"
    assert result.prediction == "impersonation"
    assert result.risk_level == "CRITICAL"
    assert result.risk_score >= 80
    assert result.confidence >= 0.5
    assert result.model_version == "impersonation-xgboost-v1"

    assert result.indicators
    assert result.explanation
    assert result.recommended_actions


def test_missing_features_rejected(detector):
    event = {
        "category": "impersonation",
        "features": {},
    }

    with pytest.raises(ValueError, match="Missing required features"):
        detector.analyze(event)


def test_missing_features_dictionary_rejected(detector):
    event = {
        "category": "impersonation",
    }

    with pytest.raises(
        ValueError,
        match="event must contain a 'features' dictionary",
    ):
        detector.analyze(event)


def test_non_dictionary_event_rejected(detector):
    with pytest.raises(TypeError, match="event must be a dictionary"):
        detector.analyze("invalid event")


def test_invalid_features_type_rejected(detector):
    event = {
        "category": "impersonation",
        "features": "invalid",
    }

    with pytest.raises(
        ValueError,
        match="event must contain a 'features' dictionary",
    ):
        detector.analyze(event)