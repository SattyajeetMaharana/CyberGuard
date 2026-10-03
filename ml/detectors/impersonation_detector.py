from ml.common.detection import Detection
from ml.common.risk import risk_level_from_score
from ml.inference.impersonation.predictor import ImpersonationPredictor
from ml.xai.impersonation.shap_explainer import ImpersonationSHAPExplainer


class ImpersonationDetector:
    """CyberGuard detector for BEC and email impersonation signals."""

    CATEGORY = "impersonation"
    MODEL_VERSION = "impersonation-xgboost-v1"

    def __init__(self) -> None:
        self.predictor = ImpersonationPredictor()
        self.explainer = ImpersonationSHAPExplainer()

    def analyze(self, event: dict) -> Detection:
        if not isinstance(event, dict):
            raise TypeError("event must be a dictionary")

        features = event.get("features")

        if not isinstance(features, dict):
            raise ValueError(
                "event must contain a 'features' dictionary"
            )

        prediction_result = self.predictor.predict(features)
        explanation_result = self.explainer.explain(features)

        probability = float(
            prediction_result["probability_impersonation"]
        )

        risk_score = probability * 100.0

        risk_level = risk_level_from_score(risk_score)

        indicators = self._build_indicators(features)

        explanation = explanation_result[
            "human_readable_explanation"
        ]

        recommended_actions = self._build_recommended_actions(
            prediction_result["prediction"],
            risk_level.value,
        )

        return Detection(
            category=self.CATEGORY,
            prediction=prediction_result["prediction"],
            risk_score=risk_score,
            risk_level=risk_level.value,
            confidence=prediction_result["confidence"],
            indicators=indicators,
            explanation=explanation,
            recommended_actions=recommended_actions,
            model_version=self.MODEL_VERSION,
        )

    @staticmethod
    def _build_indicators(features: dict) -> list[str]:
        indicators = []

        if features.get("reply_to_mismatch") == 1:
            indicators.append(
                "Reply-to domain does not match the expected sender identity"
            )

        if features.get("auth_failure") == 1:
            indicators.append(
                "Email authentication failure detected"
            )

        if features.get("full_auth_bypass") == 1:
            indicators.append(
                "Full authentication bypass detected"
            )

        if features.get("dkim_pass") == 0:
            indicators.append(
                "DKIM authentication did not pass"
            )

        if features.get("spf_pass") == 0:
            indicators.append(
                "SPF authentication did not pass"
            )

        if features.get("dmarc_pass") == 0:
            indicators.append(
                "DMARC authentication did not pass"
            )

        if features.get("requests_wire_transfer") == 1:
            indicators.append(
                "Wire-transfer request detected"
            )

        if features.get("requests_gift_cards") == 1:
            indicators.append(
                "Gift-card request detected"
            )

        if features.get("requests_sensitive_data") == 1:
            indicators.append(
                "Sensitive-data request detected"
            )

        if features.get("urgency_level", 0) >= 4:
            indicators.append(
                "High urgency communication pattern detected"
            )

        if features.get("sent_outside_hours") == 1:
            indicators.append(
                "Communication sent outside normal hours"
            )

        if features.get("requested_amount_usd", 0) > 0:
            indicators.append(
                "Financial amount requested"
            )

        if not indicators:
            indicators.append(
                "No major impersonation indicators detected"
            )

        return indicators

    @staticmethod
    def _build_recommended_actions(
        prediction: str,
        risk_level: str,
    ) -> list[str]:

        if prediction == "benign":
            return [
                "Allow communication under normal monitoring"
            ]

        if risk_level in {"HIGH", "CRITICAL"}:
            return [
                "Quarantine or block the communication",
                "Verify the sender through an independent channel",
                "Do not approve financial or sensitive-data requests",
                "Investigate the sender identity and authentication results",
            ]

        if risk_level == "MEDIUM":
            return [
                "Require additional sender verification",
                "Review authentication and reply-to information",
                "Do not act on financial requests until verified",
            ]

        return [
            "Review sender identity before responding",
            "Verify unusual requests independently",
        ]