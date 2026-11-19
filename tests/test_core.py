from collections.abc import Callable
from copy import deepcopy

import pytest

from core import (
    Student,
    add_bonus,
    average,
    compose,
    ects_category,
    make_multiplier,
    make_processor,
    passing,
    process_students_pure,
    scale_grades,
    stamp_result,
    weighted_average,
    with_result,
)


@pytest.fixture
def students() -> list[Student]:
    return [
        {"id": 1, "name": "A", "grades": [90, 85, 95]},
        {"id": 2, "name": "B", "grades": [55, 60, 50]},
        {"id": 3, "name": "C", "grades": [70, 75, 80]},
        {"id": 4, "name": "D", "grades": []},
    ]


def test_average() -> None:
    assert average([90, 85, 95]) == 90
    assert average([]) == 0.0


def test_referential_transparency(students: list[Student]) -> None:
    r1 = process_students_pure(students, pass_score=60, bonus=0)
    r2 = process_students_pure(students, pass_score=60, bonus=0)
    assert r1 == r2


def test_no_mutation(students: list[Student]) -> None:
    original = deepcopy(students)
    process_students_pure(students, pass_score=0, bonus=10)
    make_processor(
        aggregate=average,
        adjust=add_bonus(5),
        accept=passing(0),
        categorize=ects_category,
    )(students)
    assert students == original


def test_with_result_returns_new_dict(students: list[Student]) -> None:
    s = students[0]
    new = with_result(s, 90.0, "A")
    assert new is not s
    assert "final" not in s and new["final"] == 90.0


def test_pure_processing_values(students: list[Student]) -> None:
    r = process_students_pure(students, pass_score=60, bonus=0)
    assert [s["id"] for s in r["students"]] == [1, 3]
    assert [s["category"] for s in r["students"]] == ["A", "C"]
    assert r["average"] == 82.5


def test_bonus_is_capped() -> None:
    assert add_bonus(10)(95) == 100
    assert add_bonus(5)(60) == 65


def test_callable_policies(students: list[Student]) -> None:
    processor = make_processor(
        aggregate=weighted_average([1, 1, 2]),
        adjust=add_bonus(5),
        accept=passing(60),
        categorize=lambda x: "pass" if x >= 75 else "weak",
    )
    r = processor(students)
    # A: (90+85+190)/4 = 91.25 +5 = 96.25; C: (70+75+160)/4 = 76.25 +5 = 81.25
    assert [s["final"] for s in r["students"]] == [96.25, 81.25]
    assert [s["category"] for s in r["students"]] == ["pass", "pass"]
    assert r["count"] == 2


def test_policies_are_swappable(students: list[Student]) -> None:
    strict = make_processor(
        aggregate=lambda g: min(g, default=0.0),
        adjust=lambda x: x,
        accept=passing(80),
        categorize=str,
    )
    assert [s["id"] for s in strict(students)["students"]] == [1]


@pytest.mark.parametrize(
    ("score", "cat"),
    [(95, "A"), (85, "B"), (75, "C"), (65, "D"), (60, "E"), (10, "F")],
)
def test_ects(score: float, cat: str) -> None:
    assert ects_category(score) == cat


def test_stamp_result_uses_injected_clock(students: list[Student]) -> None:
    report = process_students_pure(students, pass_score=60, bonus=0)
    assert stamp_result(report, lambda: 123.0) == (report, 123.0)


def test_compose_and_multiplier() -> None:
    inc_then_double = compose(make_multiplier(2), make_multiplier(1))
    assert inc_then_double(3) == 6
    inc: Callable[[int], int] = lambda x: x + 1  # noqa: E731
    assert compose(make_multiplier(2), inc)(3) == 8


def test_scale_grades_returns_new_list() -> None:
    g = [50.0, 60.0]
    assert scale_grades(g, 1.1) == [55.0, 66.0]
    assert g == [50.0, 60.0]
