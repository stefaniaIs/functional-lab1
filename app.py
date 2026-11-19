"""Оболонка побічних ефектів: дані, друк звіту, час."""

from __future__ import annotations

import time

from core import (
    Report,
    Student,
    add_bonus,
    average,
    compose,
    ects_category,
    make_processor,
    passing,
    process_students_pure,
    stamp_result,
)

STUDENTS: list[Student] = [
    {"id": 1, "name": "Олена", "group": "ФеП-22", "grades": [90, 85, 95]},
    {"id": 2, "name": "Андрій", "group": "ФеП-22", "grades": [55, 60, 50]},
    {"id": 3, "name": "Марія", "group": "ФеП-22", "grades": [70, 75, 80]},
    {"id": 4, "name": "Ігор", "group": "ФеП-22", "grades": [58, 59, 61]},
]


def render_report(title: str, report: Report) -> None:
    print(f"== {title} ==")
    for s in report["students"]:
        print(
            f"  {s['id']:>2} {s['name']:<8} final={s['final']:6.2f} [{s['category']}]"
        )
    print(f"  Пройшли: {report['count']}, середній бал: {report['average']}")


def run() -> None:
    render_report(
        "Чиста функція (поріг 60, бонус 2)",
        process_students_pure(STUDENTS, pass_score=60, bonus=2),
    )

    processor = make_processor(
        aggregate=average,
        adjust=compose(add_bonus(5), add_bonus(0)),
        accept=passing(60),
        categorize=ects_category,
    )
    report, ts = stamp_result(processor(STUDENTS), time.time)
    render_report("Callable-політики (бонус 5)", report)
    print("Згенеровано:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)))


if __name__ == "__main__":
    run()
