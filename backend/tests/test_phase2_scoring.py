from app.scoring.aggregation import (
    department_score,
    organization_score,
)
from app.scoring.service import ScoreService


def test_score_starts_at_50():
    service = ScoreService()

    score = service.get_current_score("user-1")

    assert score.score == 50


def test_threat_decreases_score():
    service = ScoreService()

    event = service.record_score_event(
        "user-1",
        threat_detected=True,
        reason="HIGH: phishing_url",
    )

    assert event.previous_score == 50
    assert event.delta == -1
    assert event.new_score == 49
    assert event.event == "HIGH: phishing_url"


def test_safe_event_increases_score():
    service = ScoreService()

    event = service.record_score_event(
        "user-1",
        threat_detected=False,
        reason="SAFE: normal_activity",
    )

    assert event.previous_score == 50
    assert event.delta == 1
    assert event.new_score == 51


def test_score_never_exceeds_100():
    service = ScoreService()
    service._scores["user-1"] = 100

    event = service.record_score_event(
        "user-1",
        threat_detected=False,
        reason="SAFE",
    )

    assert event.previous_score == 100
    assert event.new_score == 100
    assert event.delta == 0


def test_score_never_goes_below_zero():
    service = ScoreService()
    service._scores["user-1"] = 0

    event = service.record_score_event(
        "user-1",
        threat_detected=True,
        reason="CRITICAL",
    )

    assert event.previous_score == 0
    assert event.new_score == 0
    assert event.delta == 0


def test_department_score():
    employee_scores = {
        "employee-1": 80,
        "employee-2": 60,
        "employee-3": 40,
    }

    employee_departments = {
        "employee-1": "dept-1",
        "employee-2": "dept-1",
        "employee-3": "dept-2",
    }

    result = department_score(
        employee_scores,
        employee_departments,
        "dept-1",
    )

    assert result is not None
    assert result.score == 70
    assert result.member_count == 2


def test_organization_score():
    department_scores = {
        "dept-1": 70,
        "dept-2": 50,
    }

    result = organization_score(
        department_scores,
        ["dept-1", "dept-2"],
        "org-1",
    )

    assert result is not None
    assert result.score == 60
    assert result.member_count == 2