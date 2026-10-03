from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class ScoreAggregation:
    entity_id: str
    score: float
    member_count: int


def average_score(scores: Iterable[float]) -> float | None:
    values = list(scores)

    if not values:
        return None

    return sum(values) / len(values)


def department_score(
    employee_scores: Mapping[str, float],
    employee_departments: Mapping[str, str],
    department_id: str,
) -> ScoreAggregation | None:
    scores = [
        score
        for employee_id, score in employee_scores.items()
        if employee_departments.get(employee_id) == department_id
    ]

    average = average_score(scores)

    if average is None:
        return None

    return ScoreAggregation(
        entity_id=department_id,
        score=average,
        member_count=len(scores),
    )


def organization_score(
    department_scores: Mapping[str, float],
    organization_departments: Iterable[str],
    organization_id: str,
) -> ScoreAggregation | None:
    department_ids = set(organization_departments)

    scores = [
        score
        for department_id, score in department_scores.items()
        if department_id in department_ids
    ]

    average = average_score(scores)

    if average is None:
        return None

    return ScoreAggregation(
        entity_id=organization_id,
        score=average,
        member_count=len(scores),
    )