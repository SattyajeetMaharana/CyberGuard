from datetime import datetime, UTC

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
            timestamp=datetime.now(UTC),
        )

    def calculate_score(
        self,
        current_score: int,
        *,
        threat_detected: bool,
    ) -> int:
        delta = -1 if threat_detected else 1

        return max(
            0,
            min(100, current_score + delta),
        )

    def record_score_event(
        self,
        user_id: str,
        *,
        threat_detected: bool,
        reason: str,
    ) -> ScoreEvent:
        previous_score = self._scores.get(user_id, 50)

        new_score = self.calculate_score(
            previous_score,
            threat_detected=threat_detected,
        )

        delta = new_score - previous_score

        event = ScoreEvent(
            user_id=user_id,
            previous_score=previous_score,
            delta=delta,
            new_score=new_score,
            event=reason,
            timestamp=datetime.now(UTC),
        )

        self._scores[user_id] = new_score

        self._history.setdefault(
            user_id,
            [],
        ).append(event)

        return event

    def get_score_history(
        self,
        user_id: str,
    ) -> list[ScoreEvent]:
        return list(
            self._history.get(user_id, [])
        )


score_service = ScoreService()
# Backward-compatible API for the original scoring tests.

def calculate_score(
    current_score: int,
    change: int,
) -> int:
    return max(
        0,
        min(100, current_score + change),
    )
