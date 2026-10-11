from collections.abc import Iterable

from streamstats.models import LEVELS


def analyse_events(events: Iterable[dict | None]) -> dict:
    """Собирает статистику событий и подсчитывает пропущенные записи"""
    sources = {}
    event_count, skip_count = 0, 0
    sources_error_critical = {}
    timestamp_min, timestamp_max = None, None
    levels = {}
    for i in LEVELS:
        levels[i] = 0
    for event in events:
        if event is None:
            skip_count += 1
        else:
            event_count += 1
            levels[event["level"]] += 1
            if timestamp_min is None or event["timestamp"] < timestamp_min:
                timestamp_min = event["timestamp"]
            if timestamp_max is None or event["timestamp"] > timestamp_max:
                timestamp_max = event["timestamp"]
            if event["source"] in sources:
                sources[event["source"]] += 1
            else:
                sources[event["source"]] = 1
            if event["level"] in ("ERROR", "CRITICAL"):
                if event["source"] in sources_error_critical:
                    sources_error_critical[event["source"]] += 1
                else:
                    sources_error_critical[event["source"]] = 1
    sorted_sources = sorted(sources_error_critical.items(), key=lambda x: (-x[1], x[0]))
    top_5_sources = sorted_sources[:5]
    statistics = {
        "event_count": event_count,
        "skip_count": skip_count
    }
    statistics["levels"] = levels
    statistics["sources"] = sources
    statistics["timestamp_min"] = timestamp_min
    statistics["timestamp_max"] = timestamp_max
    statistics["top_5_sources"] = top_5_sources

    return statistics
