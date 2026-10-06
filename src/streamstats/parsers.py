import csv, json
from collections.abc import Iterator
from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.models import create_event, FIELDS


def parse_jsonl(file: str) -> Iterator[dict]:
    with open(file, "r", encoding="utf-8") as f:
        for index, line in enumerate(f, start=1):
            try:
                line_dict = json.loads(line)
            except json.JSONDecodeError:
                raise InvalidEventError(f"{file}, {index}: некорректный json")

            if not isinstance(line_dict, dict):
                raise InvalidEventError(f"{file}, {index}: некорректный json")
            
            for i in FIELDS:
                if i not in line_dict:
                    raise InvalidEventError(f"{file}, {index}: отсутствует поле {i}")
                
            try:
                event = create_event(
                    line_dict["timestamp"], 
                    line_dict["level"], 
                    line_dict["source"], 
                    line_dict["message"]
                )
            except InvalidEventError as error:            
                raise InvalidEventError(f"{file}, {index}: {error}")
            except InvalidTimestampError as error:
                raise InvalidTimestampError(f"{file}, {index}: {error}")
            
            yield event







