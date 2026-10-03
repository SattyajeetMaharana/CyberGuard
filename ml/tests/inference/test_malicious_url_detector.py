import pytest

from ml.common.detection import Detection
from ml.detectors.malicious_url_detector import MaliciousURLDetector


@pytest.fixture(scope="module")
def detector():
    return MaliciousURLDetector()


def test_detector_returns_detection(detector):
    result = detector.analyze({
        "url": "https://www.google.com"
    })

    assert isinstance(result, Detection)
    assert result.category == "malicious_url"
    assert result.prediction in {"benign", "malicious"}
    assert 0.0 <= result.risk_score <= 100.0
    assert result.risk_level in {
        "SAFE",
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }
    assert 0.0 <= result.confidence <= 1.0
    assert result.model_version == "malicious-url-xgboost-v1"
    assert result.explanation
    assert result.indicators
    assert result.recommended_actions


def test_detector_identifies_known_malicious_example(detector):
    result = detector.analyze({
        "url": "http://192.168.1.1/login?verify=123456"
    })

    assert result.prediction == "malicious"
    assert result.risk_level == "CRITICAL"
    assert result.risk_score >= 80.0
    assert result.indicators
    assert result.explanation
    assert result.recommended_actions


@pytest.mark.parametrize(
    "event",
    [
        {},
        {"url": ""},
        {"url": "   "},
        {"url": None},
        {"url": 12345},
    ],
)
def test_detector_rejects_missing_or_invalid_url(detector, event):
    with pytest.raises(ValueError):
        detector.analyze(event)


def test_detector_rejects_non_dict_event(detector):
    with pytest.raises(TypeError):
        detector.analyze("https://example.com")


@pytest.mark.parametrize(
    "url",
    [
        # Very long URL
        "https://example.com/" + ("a" * 5000),

        # Unicode / internationalized URL
        "https://例子.测试/登录",

        # Shortened URL format
        "https://bit.ly/example123",

        # Suspicious domain-style URL
        "http://secure-login-account-verification.example/login?verify=true",

        # Legitimate domain with query parameters
        "https://www.google.com/search?q=cybersecurity",
    ],
)
def test_detector_handles_url_edge_cases(detector, url):
    result = detector.analyze({
        "url": url,
    })

    assert isinstance(result, Detection)
    assert result.category == "malicious_url"
    assert result.prediction in {"benign", "malicious"}

    assert 0.0 <= result.risk_score <= 100.0

    assert result.risk_level in {
        "SAFE",
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }

    assert 0.0 <= result.confidence <= 1.0
    assert result.model_version == "malicious-url-xgboost-v1"
    assert result.indicators
    assert result.explanation
    assert result.recommended_actions