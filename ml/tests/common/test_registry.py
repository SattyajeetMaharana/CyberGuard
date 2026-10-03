import pytest

from ml.common.detector_registry import (
    DetectionOrchestrator,
    DetectorRegistry,
)
from ml.detectors.impersonation_detector import ImpersonationDetector
from ml.detectors.malicious_url_detector import MaliciousURLDetector


class FakeDetector:
    def analyze(self, event: dict):
        return {
            "category": event["category"],
            "url": event.get("url"),
        }


BENIGN_IMPERSONATION_FEATURES = {
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


def test_register_and_get_detector():
    registry = DetectorRegistry()
    detector = FakeDetector()

    registry.register("malicious_url", detector)

    assert registry.get("malicious_url") is detector
    assert registry.available_categories() == ["malicious_url"]


def test_unknown_detector_raises():
    registry = DetectorRegistry()

    with pytest.raises(KeyError):
        registry.get("unknown")


def test_invalid_detector_raises():
    registry = DetectorRegistry()

    with pytest.raises(TypeError):
        registry.register("malicious_url", object())


def test_orchestrator_routes_event():
    registry = DetectorRegistry()
    registry.register("malicious_url", FakeDetector())

    orchestrator = DetectionOrchestrator(registry)

    result = orchestrator.analyze({
        "category": "malicious_url",
        "url": "https://example.com",
    })

    assert result["category"] == "malicious_url"
    assert result["url"] == "https://example.com"


def test_orchestrator_requires_category():
    registry = DetectorRegistry()
    orchestrator = DetectionOrchestrator(registry)

    with pytest.raises(ValueError):
        orchestrator.analyze({
            "url": "https://example.com"
        })


def test_orchestrator_requires_dict():
    registry = DetectorRegistry()
    orchestrator = DetectionOrchestrator(registry)

    with pytest.raises(TypeError):
        orchestrator.analyze("https://example.com")


def test_real_detectors_are_registered_and_available():
    registry = DetectorRegistry()

    registry.register(
        "malicious_url",
        MaliciousURLDetector(),
    )

    registry.register(
        "impersonation",
        ImpersonationDetector(),
    )

    assert registry.available_categories() == [
        "impersonation",
        "malicious_url",
    ]

    assert isinstance(
        registry.get("malicious_url"),
        MaliciousURLDetector,
    )

    assert isinstance(
        registry.get("impersonation"),
        ImpersonationDetector,
    )


def test_orchestrator_routes_to_real_impersonation_detector():
    registry = DetectorRegistry()

    registry.register(
        "impersonation",
        ImpersonationDetector(),
    )

    orchestrator = DetectionOrchestrator(registry)

    result = orchestrator.analyze({
        "category": "impersonation",
        "features": BENIGN_IMPERSONATION_FEATURES,
    })

    assert result.category == "impersonation"
    assert result.prediction == "benign"
    assert result.risk_level == "SAFE"
    assert result.model_version == "impersonation-xgboost-v1"


def test_orchestrator_routes_to_real_malicious_url_detector():
    registry = DetectorRegistry()

    registry.register(
        "malicious_url",
        MaliciousURLDetector(),
    )

    orchestrator = DetectionOrchestrator(registry)

    result = orchestrator.analyze({
        "category": "malicious_url",
        "url": "http://192.168.1.1/login?verify=123456",
    })

    assert result.category == "malicious_url"
    assert result.prediction == "malicious"
    assert result.risk_level == "CRITICAL"
    assert result.model_version == "malicious-url-xgboost-v1"