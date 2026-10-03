from ml.common.detection import Detector


class DetectorRegistry:
    """Registry for CyberGuard detection modules."""

    def __init__(self):
        self._detectors: dict[str, Detector] = {}

    def register(self, category: str, detector: Detector) -> None:
        if not isinstance(category, str) or not category.strip():
            raise ValueError("category must be a non-empty string")

        if not hasattr(detector, "analyze") or not callable(detector.analyze):
            raise TypeError(
                "detector must provide an analyze(event) method"
            )

        self._detectors[category] = detector

    def get(self, category: str) -> Detector:
        if category not in self._detectors:
            raise KeyError(
                f"No detector registered for category: {category}"
            )

        return self._detectors[category]

    def available_categories(self) -> list[str]:
        return sorted(self._detectors.keys())


class DetectionOrchestrator:
    """Routes events to the detector registered for their category."""

    def __init__(self, registry: DetectorRegistry):
        self.registry = registry

    def analyze(self, event: dict):
        if not isinstance(event, dict):
            raise TypeError("event must be a dictionary")

        category = event.get("category")

        if not isinstance(category, str) or not category.strip():
            raise ValueError(
                "event must contain a non-empty 'category'"
            )

        detector = self.registry.get(category)

        return detector.analyze(event)
