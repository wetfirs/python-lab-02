from datetime import datetime

from streamstats.errors import InvalidEventError, InvalidTimestampError

FIELDS = ("timestamp", "level", "source", "message")
LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def create_event(timestamp: object, level: object, source: object, message: object) -> dict:
    if not isinstance(timestamp, str):
        raise InvalidTimestampError(f"timestamp {timestamp} должен быть строкой")
    try:
        timestamp = datetime.fromisoformat(timestamp)
    except ValueError:
        raise InvalidTimestampError(f"timestamp {timestamp} некорректный")
    if level not in LEVELS:
        raise InvalidEventError(f"level {level} некорректный")
    if not isinstance(source, str) or source.strip() == "":
        raise InvalidEventError(f"source {source} некорректный")
    if not isinstance(message, str):
        raise InvalidEventError(f"message {message} некорректный")
    event = {"timestamp": timestamp,
            "level": level,
            "source": source,
            "message": message
            }
    return event
