from app.scoring.service import ScoreService


def test_initial_score():
    service = ScoreService()
    assert service.get_current_score("user1").score == 50


def test_no_threat_increases_score():
    service = ScoreService()
    event = service.record_score_event(
        "user1",
        threat_detected=False,
        reason="No threat detected",
    )
    assert event.change == 1
    assert service.get_current_score("user1").score == 51


def test_threat_decreases_score():
    service = ScoreService()
    event = service.record_score_event(
        "user1",
        threat_detected=True,
        reason="Threat detected",
    )
    assert event.change == -1
    assert service.get_current_score("user1").score == 49


def test_score_lower_bound():
    service = ScoreService()
    service._scores["user1"] = 0
    service.record_score_event(
        "user1",
        threat_detected=True,
        reason="Threat detected",
    )
    assert service.get_current_score("user1").score == 0


def test_score_upper_bound():
    service = ScoreService()
    service._scores["user1"] = 100
    service.record_score_event(
        "user1",
        threat_detected=False,
        reason="No threat detected",
    )
    assert service.get_current_score("user1").score == 100