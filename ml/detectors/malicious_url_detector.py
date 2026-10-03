from ml.common.detection import Detection
from ml.common.risk import risk_level_from_score
from ml.inference.malicious_url.predictor import MaliciousURLPredictor
from ml.xai.malicious_url.shap_explainer import MaliciousURLSHAPExplainer


class MaliciousURLDetector:
    """Production-facing detector wrapping the Phase 1 URL model."""

    category = "malicious_url"

    def __init__(self):
        self.predictor = MaliciousURLPredictor()
        self.explainer = MaliciousURLSHAPExplainer()

    def analyze(self, event: dict) -> Detection:
        if not isinstance(event, dict):
            raise TypeError("event must be a dictionary")

        url = event.get("url")

        if not isinstance(url, str) or not url.strip():
            raise ValueError("event must contain a non-empty string 'url'")

        result = self.predictor.predict(url)

        risk_score = result["probability_malicious"] * 100.0
        risk_level = risk_level_from_score(risk_score)

        indicators = self._build_indicators(result["features"])

        shap_explanation = self.explainer.explain(url)
        explanation = self._build_explanation(
            result,
            shap_explanation,
        )

        recommended_actions = self._recommended_actions(
            result["prediction"],
            risk_level.value,
        )

        return Detection(
            category=self.category,
            prediction=result["prediction"],
            risk_score=risk_score,
            risk_level=risk_level.value,
            confidence=result["confidence"],
            indicators=indicators,
            explanation=explanation,
            recommended_actions=recommended_actions,
            model_version=result["model_version"],
        )

    @staticmethod
    def _build_indicators(features: dict) -> list[str]:
        indicators = []

        if features.get("IsDomainIP") == 1:
            indicators.append("URL uses an IP address instead of a domain")

        if features.get("HasObfuscation") == 1:
            indicators.append("URL contains obfuscation patterns")

        if features.get("NoOfSubDomain", 0) >= 3:
            indicators.append("URL contains multiple subdomains")

        if features.get("NoOfQMark", 0) > 0:
            indicators.append("URL contains query parameters")

        if features.get("NoOfEqualsInURL", 0) > 0:
            indicators.append("URL contains parameter assignment characters")

        if features.get("NoOfAmpersandInURL", 0) > 0:
            indicators.append("URL contains multiple query parameters")

        if features.get("NoOfOtherSpecialCharsInURL", 0) > 0:
            indicators.append("URL contains special characters")

        if features.get("IsHTTPS") == 0:
            indicators.append("URL does not use HTTPS")

        if not indicators:
            indicators.append("No high-risk URL structural indicators detected")

        return indicators

    @staticmethod
    def _build_explanation(result: dict, shap_explanation) -> str:
        contributions = sorted(
            shap_explanation.feature_contributions,
            key=lambda item: abs(item.contribution),
            reverse=True,
        )

        top = contributions[:3]

        parts = [
            f"Model predicted {result['prediction']} "
            f"with {result['probability_malicious']:.2%} malicious probability."
        ]

        if top:
            feature_text = ", ".join(
                f"{item.feature}={item.value:g} "
                f"(contribution {item.contribution:+.3f})"
                for item in top
            )
            parts.append(
                f"Top SHAP contributors were: {feature_text}."
            )

        return " ".join(parts)

    @staticmethod
    def _recommended_actions(
        prediction: str,
        risk_level: str,
    ) -> list[str]:
        if prediction == "malicious":
            if risk_level == "CRITICAL":
                return [
                    "Block or quarantine the URL",
                    "Do not open the URL",
                    "Investigate the source of the URL",
                ]

            if risk_level in {"HIGH", "MEDIUM"}:
                return [
                    "Avoid opening the URL",
                    "Investigate the URL source",
                ]

            return [
                "Exercise caution before opening the URL",
            ]

        return [
            "URL classified as benign by the current model",
            "Continue normal security precautions",
        ]
