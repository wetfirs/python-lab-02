import json


def to_json(output_file: str, statistics: dict) -> None:
    stat_copy = statistics.copy()
    if stat_copy["timestamp_min"] is not None:
        stat_copy["timestamp_min"] = stat_copy["timestamp_min"].isoformat()
    if stat_copy["timestamp_max"] is not None:
        stat_copy["timestamp_max"] = stat_copy["timestamp_max"].isoformat()
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(stat_copy, f, ensure_ascii=False, indent=4)
