# Лабораторна робота №1 — Основи ФП у Python

**Варіант 3. Обробка результатів студентів.** Іщенко Стефанія, ФеП-22.

Вхід: студенти з оцінками за модулі. Обчислюється підсумковий бал (середній),
застосовується бонус, відбираються студенти з прохідним балом, кожному
присвоюється категорія ECTS (A–F).

## Структура
| Файл | Що всередині |
|---|---|
| `starter_imperative.py` | імперативний «поганий» варіант для порівняння (глобал, print, мутації) |
| `core.py` | **чисте ядро**: `average`, `weighted_average`, `add_bonus`, `passing`, `ects_category`, `with_result`, `process_students_pure`, фабрика `make_processor`, `stamp_result`, `compose`, `make_multiplier`, `scale_grades` |
| `app.py` | оболонка I/O: дані, `render_report` (print), реальний час |
| `tests/test_core.py` | pytest: референтна прозорість, немутація, Callable-політики |

## Що зроблено
- **Завдання 1:** `process_students_pure` — всі параметри (`pass_score`, `bonus`) явно, без глобалів, повертає нові словники (`with_result` робить `{**s, ...}`).
- **Завдання 2:** `make_processor(aggregate=, adjust=, accept=, categorize=)` — 4 політики через `typing.Callable`; функція вищого порядку повертає налаштований обробник.
- **Завдання 3:** весь `print` — в `app.py`; час передається у `stamp_result` як `NowFn` (інжекція залежності).
- Додатково: `compose`, `make_multiplier`, `scale_grades` (новий список замість мутації).

## Запуск
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
mypy core.py app.py tests
black --check core.py app.py tests && ruff check core.py app.py tests
python app.py
```
