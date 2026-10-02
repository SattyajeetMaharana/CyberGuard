import pytest

from ml.common.test_detector import TestDetector


def test_detector_safe_event():
    detector = TestDetector()

    result = detector.analyze({
        "is_threat": False
    })

    assert result.category == "test"
    assert result.prediction == "safe"
    assert result.risk_score == 10
    assert result.risk_level == "SAFE"
    assert result.confidence == 0.98
    assert result.model_version == "test-detector-v1"


def test_detector_threat_event():
    detector = TestDetector()

    result = detector.analyze({
        "is_threat": True
    })

    assert result.category == "test"
    assert result.prediction == "threat"
    assert result.risk_score == 90
    assert result.risk_level == "CRITICAL"
    assert result.confidence == 0.95
    assert result.model_version == "test-detector-v1"


def test_detector_returns_detection_object():
    detector = TestDetector()

    result = detector.analyze({
        "is_threat": True
    })

    assert hasattr(result, "category")
    assert hasattr(result, "prediction")
    assert hasattr(result, "risk_score")
    assert hasattr(result, "risk_level")
    assert hasattr(result, "confidence")
    assert hasattr(result, "indicators")
    assert hasattr(result, "explanation")
    assert hasattr(result, "recommended_actions")
    assert hasattr(result, "model_version")


def test_detector_rejects_invalid_event():
    detector = TestDetector()

    with pytest.raises(TypeError):
        detector.analyze("invalid event")