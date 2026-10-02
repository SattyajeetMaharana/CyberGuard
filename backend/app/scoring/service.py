from datetime import datetime

from .contracts import CyberScore, ScoreEvent


class ScoreService:
    def __init__(self):
        self._scores: dict[str, int] = {}
        self._history: dict[str, list[ScoreEvent]] = {}

    def get_current_score(self, user_id: str) -> CyberScore:
        score = self._scores.get(user_id, 50)

        return CyberScore(
            user_id=user_id,
            score=score,
            timestamp=datetime.utcnow(),
        )

    def calculate_score(
        self,
        current_score: int,
        *,
        threat_detected: bool,
    ) -> int:
        change = -1 if threat_detected else 1

        return max(0, min(100, current_score + change))

    def record_score_event(
        self,
        user_id: str,
        *,
        threat_detected: bool,
        reason: str,
    ) -> ScoreEvent:
        current = self._scores.get(user_id, 50)

        new_score = self.calculate_score(
            current,
            threat_detected=threat_detected,
        )

        change = new_score - current

        event = ScoreEvent(
            user_id=user_id,
            change=change,
            reason=reason,
            timestamp=datetime.utcnow(),
        )

        self._scores[user_id] = new_score
        self._history.setdefault(user_id, []).append(event)

        return event

    def get_score_history(self, user_id: str) -> list[ScoreEvent]:
        return list(self._history.get(user_id, []))


score_service = ScoreService()