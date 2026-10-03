from __future__ import annotations

from typing import Any, Protocol

from app.services.detection_orchestrator import DetectorResult


class MaliciousURLPredictorProtocol(Protocol):
    """Protocol for the malicious URL ML predictor."""

    def predict(self, url: str) -> dict[str, Any]:
        ...


class MaliciousURLDetector:
    """
    Backend adapter for the CyberGuard malicious URL predictor.

    Converts the ML predictor output into the backend's
    standard DetectorResult contract.
    """

    def __init__(
        self,
        predictor: MaliciousURLPredictorProtocol | None = None,
    ) -> None:
        if predictor is None:
            from ml.inference.malicious_url.predictor import (
                MaliciousURLPredictor,
            )

            predictor = MaliciousURLPredictor()

        self.predictor = predictor

    def analyze(self, event: dict[str, Any]) -> DetectorResult:
        """
        Analyze a normalized CyberGuard URL-analysis event.

        Expected event payload:

            {
                "payload": {
                    "url": "https://example.com"
                }
            }
        """

        payload = event.get("payload") or {}
        url = payload.get("url")

        if not isinstance(url, str) or not url.strip():
            raise ValueError(
                "URL analysis event does not contain a valid URL"
            )

        url = url.strip()

        result = self.predictor.predict(url)

        prediction = str(
            result.get("prediction", "")
        ).strip().lower()

        if prediction not in {"malicious", "benign"}:
            raise ValueError(
                f"Invalid malicious URL predictor output: {prediction!r}"
            )

        probability_malicious = float(
            result.get("probability_malicious", 0.0)
        )

        confidence = float(
            result.get("confidence", 0.0)
        )

        probability_malicious = max(
            0.0,
            min(1.0, probability_malicious),
        )

        confidence = max(
            0.0,
            min(1.0, confidence),
        )

        # Risk score always represents the probability that
        # the URL is malicious.
        risk_score = probability_malicious * 100.0

        category = (
            "malicious_url"
            if prediction == "malicious"
            else "benign_url"
        )

        risk_level = self._risk_level(risk_score)

        if prediction == "malicious":
            recommended_actions = [
                "Do not open the URL",
                "Verify the domain before continuing",
            ]
        else:
            recommended_actions = []

        indicators = [
            f"malicious_probability={probability_malicious:.4f}",
        ]

        explanation = (
            f"Malicious URL model predicted '{prediction}' "
            f"with confidence {confidence:.4f}."
        )

        return DetectorResult(
            category=category,
            prediction=prediction,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=confidence,
            indicators=indicators,
            explanation=explanation,
            recommended_actions=recommended_actions,
            model_version=str(
                result.get(
                    "model_version",
                    "unknown",
                )
            ),
            detector_version=str(
                result.get(
                    "feature_version",
                    "unknown",
                )
            ),
        )

    @staticmethod
    def _risk_level(risk_score: float) -> str:
        """Convert a 0-100 risk score into CyberGuard risk levels."""

        if risk_score >= 80:
            return "CRITICAL"

        if risk_score >= 60:
            return "HIGH"

        if risk_score >= 40:
            return "MEDIUM"

        if risk_score >= 20:
            return "LOW"

        return "SAFE"