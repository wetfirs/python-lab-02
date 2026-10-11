from datetime import datetime

from streamstats.analysis import analyse_events
from streamstats.parsers import parse_csv, parse_jsonl


def test_csv_jsonl_same_statistics(tmp_path):
    csv_file = tmp_path / "events.csv"
    jsonl_file = tmp_path / "events.jsonl"
    csv_file.write_text("timestamp,level,source,message\n" 
    "2026-09-15T15:00:00,DEBUG,site,сообщение\n",
    encoding="utf-8",
    )
    jsonl_file.write_text('{"timestamp": "2026-09-15T15:00:00", "level": "DEBUG", "source": "site", "message": "сообщение"}\n',
            encoding="utf-8",
    )
    csv_statistics = analyse_events(parse_csv(str(csv_file)))
    jsonl_statistics = analyse_events(parse_jsonl(str(jsonl_file)))
    
    assert csv_statistics == jsonl_statistics


def test_analyse_events_counts():
    events = [
        {"timestamp": datetime(2026, 10, 11, 12),
            "level": "INFO",
            "source": "app",
            "message": "111",
        },
        {"timestamp": datetime(2026, 10, 11, 7),
            "level": "ERROR",
            "source": "payment",
            "message": "222",
        },
        None,
        {"timestamp": datetime(2026, 10, 11, 14),
            "level": "CRITICAL",
            "source": "app",
            "message": "333",
        }
    ]
    statistics = analyse_events(events)
    assert statistics["event_count"] == 3
    assert statistics["skip_count"] == 1
    assert statistics["sources"] == {"app": 2, "payment": 1}
    assert statistics["levels"] == {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 0,
        "ERROR": 1,
        "CRITICAL": 1,
    }
    assert statistics["timestamp_min"] == datetime(2026, 10, 11, 7)
    assert statistics["timestamp_max"] == datetime(2026, 10, 11, 14)
    assert statistics["top_5_sources"] == [("app", 1), ("payment", 1)]


def test_analyse_events_empty():
    statistics = analyse_events([])
    assert statistics["event_count"] == 0
    assert statistics["skip_count"] == 0
    assert statistics["sources"] == {}
    assert statistics["levels"] == {
        "DEBUG": 0,
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0,
    }
    assert statistics["timestamp_min"] is None
    assert statistics["timestamp_max"] is None
    assert statistics["top_5_sources"] == []