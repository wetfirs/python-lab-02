from datetime import datetime

import pytest

from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.parsers import parse_csv, parse_jsonl


def test_parse_jsonl(tmp_path):
    input_file = tmp_path / "events.jsonl"
    input_file.write_text(
        '{"timestamp": "2026-10-08T10:00:00", "level": "INFO", "source": "app", "message": "hello"}\n',
        encoding="utf-8",
    )
    events = list(parse_jsonl(str(input_file)))
    assert len(events) == 1
    assert events[0]["message"] == "hello"
    assert events[0]["source"] == "app"
    assert events[0]["level"] == "INFO"
    assert events[0]["timestamp"] == datetime(2026, 10, 8, 10, 0, 0)


def test_parse_csv(tmp_path):
    input_file = tmp_path / "events.csv"
    input_file.write_text("timestamp,level,source,message\n" \
    "2026-09-15T15:00:00,DEBUG,site,hi\n",
    encoding="utf-8",
    )
    events = list(parse_csv(str(input_file)))
    assert len(events) == 1
    assert events[0]["message"] == "hi"
    assert events[0]["source"] == "site"
    assert events[0]["level"] == "DEBUG"
    assert events[0]["timestamp"] == datetime(2026, 9, 15, 15, 0, 0)


def test_parse_jsonl_empty(tmp_path):
    input_file = tmp_path / "events.jsonl"
    input_file.write_text("", encoding="utf-8")
    events = list(parse_jsonl(str(input_file)))
    assert events == []


def test_parse_csv_empty(tmp_path):
    input_file = tmp_path / "events.csv"
    input_file.write_text("", encoding="utf-8")
    events = list(parse_csv(str(input_file)))
    assert events == []


def test_parse_jsonl_without_source(tmp_path):
    input_file = tmp_path / "events.jsonl"
    input_file.write_text('{"timestamp": "2020-02-06T10:10:10", "level": "ERROR", "message": "hello"}\n',
            encoding="utf-8",
    ) 
    with pytest.raises(InvalidEventError):
        list(parse_jsonl(str(input_file)))


def test_parse_csv_without_message(tmp_path):
    input_file = tmp_path / "events.csv"
    input_file.write_text("timestamp,level,source\n" \
    "2026-09-15T15:00:00,DEBUG,site\n",
    encoding="utf-8",
    )
    with pytest.raises(InvalidEventError):
        list(parse_csv(str(input_file)))


def test_parse_jsonl_incorrect_timestamp_skip_invalid(tmp_path):
    input_file = tmp_path / "events.jsonl"
    input_file.write_text('{"timestamp": "2026/09/22", "level": "ERROR", "source": "app", "message": "ошибка"}\n'
                          '{"timestamp": "2026-09-22T10:10:10", "level": "WARNING", "source": "app", "message": "после ошибки"}\n',
                encoding="utf-8",
    )
    events = list(parse_jsonl(str(input_file), skip_invalid=True))
    assert len(events) == 2
    assert events[0] is None
    assert events[1]["message"] == "после ошибки"


def test_parse_csv_incorrect_level_skip_invalid(tmp_path):
    input_file = tmp_path / "events.csv"
    input_file.write_text("timestamp,level,source,message\n"
    "2026-09-15T15:00:00,invalid,site,ошибка\n"
    "2026-09-15T15:00:00,INFO,site,нет ошибки\n",
    encoding="utf-8",
    )
    events = list(parse_csv(str(input_file), skip_invalid=True))
    assert len(events) == 2
    assert events[0] is None
    assert events[1]["message"] == "нет ошибки"


def test_parse_jsonl_invalid_timestamp(tmp_path):
    input_file = tmp_path / "events.jsonl"
    input_file.write_text('{"timestamp": "2026/09/22", "level": "ERROR", "source": "app", "message": "ошибка"}\n',
                    encoding="utf-8",
    )
    with pytest.raises(InvalidTimestampError) as error:
        list(parse_jsonl(str(input_file)))
    message = str(error.value)
    assert "timestamp" in message
    assert f"{input_file}, 1:" in message

def test_parse_jsonl_invalid_line_7(tmp_path):
    input_file = tmp_path / "events.jsonl"
    valid_line = '{"timestamp": "2026-10-08T10:00:00", "level": "INFO", "source": "app", "message": "hello"}\n'
    input_file.write_text(
        valid_line * 6 + '{"timestamp":}\n', # поврежденный json
        encoding = "utf-8",
    )
    with pytest.raises(InvalidEventError) as error:
        list(parse_jsonl(str(input_file)))
    assert f"{input_file}, 7:" in str(error.value)

def test_parse_jsonl_invalid_json_skip(tmp_path):
    input_file = tmp_path / "events.jsonl"
    input_file.write_text(
        '{"timestamp:}\n' # поврежденный json
        '{"timestamp": "2026-10-08T10:00:00", "level": "ERROR", "source": "app", "message": "после ошибки"}\n',
        encoding="utf-8",
    )
    events = list(parse_jsonl(str(input_file), skip_invalid=True))
    assert len(events) == 2
    assert events[0] is None
    assert events[1]["message"] == "после ошибки"

