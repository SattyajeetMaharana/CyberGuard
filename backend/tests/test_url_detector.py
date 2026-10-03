from __future__ import annotations

from app.services.url_detector import MaliciousURLDetector


class FakePredictor:
    def __init__(self, result: dict) -> None:
        self.result = result
        self.received_url: str | None = None

    def predict(self, url: str) -> dict:
        self.received_url = url
        return self.result


def test_malicious_prediction_is_converted_to_detector_result() -> None:
    predictor = FakePredictor(
        {
            "prediction": "malicious",
            "probability_malicious": 0.94,
            "probability_benign": 0.06,
            "confidence": 0.94,
            "model_version": "malicious-url-xgboost-v1",
            "feature_version": "malicious-url-url-only-v1",
        }
    )

    detector = MaliciousURLDetector(predictor=predictor)

    result = detector.analyze(
        {
            "payload": {
                "url": "https://example.com/login",
            }
        }
    )

    assert predictor.received_url == "https://example.com/login"
    assert result.prediction == "malicious"
    assert result.category == "malicious_url"
    assert result.risk_score == 94.0
    assert result.risk_level == "CRITICAL"
    assert result.confidence == 0.94
    assert result.model_version == "malicious-url-xgboost-v1"
    assert result.detector_version == "malicious-url-url-only-v1"


def test_benign_prediction_is_converted_to_detector_result() -> None:
    predictor = FakePredictor(
        {
            "prediction": "benign",
            "probability_malicious": 0.02,
            "probability_benign": 0.98,
            "confidence": 0.98,
            "model_version": "malicious-url-xgboost-v1",
            "feature_version": "malicious-url-url-only-v1",
        }
    )

    detector = MaliciousURLDetector(predictor=predictor)

    result = detector.analyze(
        {
            "payload": {
                "url": "https://www.google.com",
            }
        }
    )

    assert result.prediction == "benign"
    assert result.category == "benign_url"
    assert result.risk_score == 2.0
    assert result.risk_level == "SAFE"
    assert result.confidence == 0.98


def test_invalid_event_url_is_rejected() -> None:
    predictor = FakePredictor(
        {
            "prediction": "benign",
            "probability_malicious": 0.01,
            "confidence": 0.99,
        }
    )

    detector = MaliciousURLDetector(predictor=predictor)

    try:
        detector.analyze(
            {
                "payload": {},
            }
        )
    except ValueError as exc:
        assert "valid URL" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_invalid_predictor_prediction_is_rejected() -> None:
    predictor = FakePredictor(
        {
            "prediction": "unknown",
            "probability_malicious": 0.50,
            "confidence": 0.50,
        }
    )

    detector = MaliciousURLDetector(predictor=predictor)

    try:
        detector.analyze(
            {
                "payload": {
                    "url": "https://example.com",
                }
            }
        )
    except ValueError as exc:
        assert "Invalid malicious URL predictor output" in str(exc)
    else:
        raise AssertionError("Expected ValueError")