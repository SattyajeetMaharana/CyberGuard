from ml.common.detection import Detection
from ml.common.risk import risk_level_from_score


class TestDetector:
    """
    Simple detector used only to verify the common detector interface.

    This is NOT a production security model.
    """

    def analyze(self, event: dict) -> Detection:
        if not isinstance(event, dict):
            raise TypeError("event must be a dictionary")

        is_threat = bool(event.get("is_threat", False))

        if is_threat:
            risk_score = 90
            prediction = "threat"
            confidence = 0.95
            indicators = ["test threat indicator"]
            explanation = "Test detector identified a simulated threat."
            recommended_actions = ["Block and investigate the event."]
        else:
            risk_score = 10
            prediction = "safe"
            confidence = 0.98
            indicators = []
            explanation = "Test detector identified a simulated safe event."
            recommended_actions = ["No action required."]

        risk_level = risk_level_from_score(risk_score)

        return Detection(
            category="test",
            prediction=prediction,
            risk_score=risk_score,
            risk_level=risk_level.value,
            confidence=confidence,
            indicators=indicators,
            explanation=explanation,
            recommended_actions=recommended_actions,
            model_version="test-detector-v1",
        )