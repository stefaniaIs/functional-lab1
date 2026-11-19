"""Чисте ядро: обробка результатів студентів (варіант 3).

Жодного I/O, жодних глобальних змінних у розрахунках, жодних мутацій
вхідних даних - лише нові об'єкти.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import TypedDict, TypeVar


class Student(TypedDict, total=False):
    id: int
    name: str
    group: str
    grades: list[float]  # оцінки за модулі (0..100)
    final: float  # з'являється в результаті
    category: str  # з'являється в результаті


class Report(TypedDict):
    count: int
    average: float
    students: list[Student]


# --- типи політик -----------------------------------------------------------
AggregateFn = Callable[[Sequence[float]], float]  # оцінки -> підсумковий бал
AdjustFn = Callable[[float], float]  # бал -> скоригований бал (бонус/штраф)
FilterFn = Callable[[float], bool]  # бал -> чи прохідний
CategoryFn = Callable[[float], str]  # бал -> категорія успішності
NowFn = Callable[[], float]

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


# --- чисті доменні функції --------------------------------------------------
def average(grades: Sequence[float]) -> float:
    """Середнє арифметичне; для порожнього списку - 0.0."""
    return sum(grades) / len(grades) if grades else 0.0


def weighted_average(weights: Sequence[float]) -> AggregateFn:
    """Фабрика: зважене середнє (ваги модулів передаються явно)."""

    def _agg(grades: Sequence[float]) -> float:
        pairs = list(zip(grades, weights, strict=False))
        total_w = sum(w for _, w in pairs)
        return sum(g * w for g, w in pairs) / total_w if total_w else 0.0

    return _agg


def add_bonus(bonus: float, cap: float = 100.0) -> AdjustFn:
    """Фабрика: додає бонус, але не більше за cap."""
    return lambda score: min(cap, score + bonus)


def passing(min_score: float) -> FilterFn:
    """Фабрика фільтра: бал >= min_score."""
    return lambda score: score >= min_score


def ects_category(score: float) -> str:
    """Категорія успішності за шкалою ECTS."""
    if score >= 90:
        return "A"
    if score >= 82:
        return "B"
    if score >= 74:
        return "C"
    if score >= 64:
        return "D"
    if score >= 60:
        return "E"
    return "F"


def with_result(student: Student, final: float, category: str) -> Student:
    """Повертає НОВИЙ словник із полями final і category."""
    return {**student, "final": round(final, 2), "category": category}


def make_report(students: Sequence[Student]) -> Report:
    finals = [s.get("final", 0.0) for s in students]
    return {
        "count": len(students),
        "average": round(average(finals), 2),
        "students": list(students),
    }


# --- Завдання 1: чиста версія з явними параметрами --------------------------
def process_students_pure(
    students: Iterable[Student],
    *,
    pass_score: float,
    bonus: float,
) -> Report:
    scored = ((s, min(100.0, average(s.get("grades", [])) + bonus)) for s in students)
    passed = [
        with_result(s, score, ects_category(score))
        for s, score in scored
        if score >= pass_score
    ]
    return make_report(passed)


# --- Завдання 2: параметризація через Callable ------------------------------
def make_processor(
    *,
    aggregate: AggregateFn,
    adjust: AdjustFn,
    accept: FilterFn,
    categorize: CategoryFn,
) -> Callable[[Iterable[Student]], Report]:
    """Функція вищого порядку: повертає налаштований обробник."""

    def process(students: Iterable[Student]) -> Report:
        scored = ((s, adjust(aggregate(s.get("grades", [])))) for s in students)
        passed = [
            with_result(s, score, categorize(score))
            for s, score in scored
            if accept(score)
        ]
        return make_report(passed)

    return process


# --- Завдання 3: інжекція "часу" ззовні ---------------------------------------
def stamp_result(report: Report, now: NowFn) -> tuple[Report, float]:
    """Чиста щодо report; час приходить ззовні як залежність."""
    return report, now()


# --- Додаткові вправи --------------------------------------------------------
def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    return lambda x: f(g(x))


def make_multiplier(k: int) -> Callable[[int], int]:
    return lambda x: x * k


def scale_grades(grades: Sequence[float], factor: float) -> list[float]:
    """Замість мутації списку в циклі - новий список через comprehension."""
    return [round(g * factor, 2) for g in grades]
