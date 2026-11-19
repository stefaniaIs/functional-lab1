"""Стартовий ІМПЕРАТИВНИЙ варіант (для порівняння, так робити НЕ треба).

Проблеми: глобальний PASS_SCORE, print усередині обчислень,
мутація вхідних словників (s["final"] = ...), змішані обчислення та I/O.
"""

PASS_SCORE = 60  # глобальний стан


def process_students(students, bonus):  # type: ignore[no-untyped-def]
    passed = []
    total = 0.0
    for s in students:
        print("Processing student:", s["id"])  # побічний ефект
        avg = 0.0
        for g in s["grades"]:
            avg += g
        avg = avg / len(s["grades"]) if s["grades"] else 0.0
        avg = min(100.0, avg + bonus)
        if avg < PASS_SCORE:
            continue
        s["final"] = avg  # мутуємо вхідні дані
        passed.append(s)
        total += avg
    return {"count": len(passed), "avg": total / len(passed) if passed else 0.0}
