from ml.common.detection import Detection


def test_detection_contract():
    detection = Detection(
        category="phishing",
        prediction="phishing",
        risk_score=85,
        risk_level="CRITICAL",
        confidence=0.95,
        indicators=["suspicious link", "urgent language"],
        explanation="Suspicious characteristics detected.",
        recommended_actions=["Do not open the link."],
        model_version="phishing-v1",
    )

    assert detection.category == "phishing"
    assert detection.prediction == "phishing"
    assert detection.risk_score == 85
    assert detection.risk_level == "CRITICAL"
    assert detection.confidence == 0.95
    assert len(detection.indicators) == 2
    assert detection.model_version == "phishing-v1"


def test_detection_defaults():
    detection = Detection(
        category="test",
        prediction="safe",
        risk_score=10,
        risk_level="SAFE",
        confidence=0.90,
    )

    assert detection.indicators == []
    assert detection.explanation == ""
    assert detection.recommended_actions == []
    assert detection.model_version == ""
