from app.scoring.service import calculate_score


def test_score_increases():
    assert calculate_score(50, 1) == 51


def test_score_decreases():
    assert calculate_score(50, -1) == 49


def test_score_stays_within_range():
    assert calculate_score(100, 10) == 100
    assert calculate_score(0, -10) == 0