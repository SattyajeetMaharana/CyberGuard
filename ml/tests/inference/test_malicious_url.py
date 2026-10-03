"""Tests for malicious URL inference."""

from ml.inference.malicious_url.predictor import MaliciousURLPredictor


def test_malicious_url_predictor_returns_valid_result():
    predictor = MaliciousURLPredictor()

    result = predictor.predict(
        "https://www.google.com"
    )

    assert result["prediction"] in {"benign", "malicious"}
    assert 0.0 <= result["probability_malicious"] <= 1.0
    assert 0.0 <= result["probability_benign"] <= 1.0
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["model_version"] == "malicious-url-xgboost-v1"
    assert result["feature_version"] == "malicious-url-url-only-v1"


def test_malicious_url_predictor_extracts_all_features():
    predictor = MaliciousURLPredictor()

    result = predictor.predict(
        "http://192.168.1.1/login?verify=123456"
    )

    assert len(result["features"]) == 18
    assert result["prediction"] == "malicious"
