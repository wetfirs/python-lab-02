# StreamStats: потоковый анализатор файлов

Консольное приложение для чтения событий из CSV и JSONL и формирования статистики

## Возможности

- Построчное чтение файлов
- Объединение статистики нескольких файлов
- Подсчёт событий по уровням и источникам
- Top-5 источников ошибок ERROR/CRITICAL
- Первая и последняя временная метка
- Сохранение отчёта в JSON
- Пропуск ошибочных записей с `--skip-invalid`

## Основные функции

### models.py

- `create_event` — проверяет поля события и преобразует дату

### parsers.py

- `parse_csv` — читает события из CSV
- `parse_jsonl` — читает события из JSONL

### analysis.py

- `analyse_events` — собирает статистику

### report.py

- `to_json` — сохраняет JSON-отчёт

### \_\_main\_\_.py

- `read_events` — объединяет события нескольких файлов
- `main` — обрабатывает аргументы и запускает анализ

## Структура проекта

```text
.
├── src/streamstats/
│   ├── __init__.py
│   ├── __main__.py
│   ├── models.py
│   ├── parsers.py
│   ├── analysis.py
│   ├── report.py
│   └── errors.py
├── tests/
│   ├── test_parsers.py
│   ├── test_analysis.py
│   └── test_cli.py
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Запуск

Установка зависимостей:

```bash
uv sync
```

Активация окружения:

```bash
source .venv/bin/activate
```

CLI:

```bash
python -m streamstats analyze INPUT [INPUT ...] --format csv|jsonl --output REPORT.json
```

```bash
python -m streamstats analyze INPUT --format jsonl --skip-invalid
```

Справка:

```bash
python -m streamstats --help
```

## Тестирование:

```bash
python -m pytest -v
```

## Проверка качества кода:

```bash
ruff check .
```