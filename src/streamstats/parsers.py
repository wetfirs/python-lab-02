import json
import csv
import logging
from collections.abc import Iterator
from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.models import create_event, FIELDS


def parse_jsonl(file: str, skip_invalid: bool = False) -> Iterator[dict | None]:
    with open(file, "r", encoding="utf-8") as f:
        for index, line in enumerate(f, start=1):
            try:
                line_dict = json.loads(line)

                if not isinstance(line_dict, dict):
                    raise InvalidEventError("некорректный json")
                
                for i in FIELDS:
                    if i not in line_dict:
                        raise InvalidEventError(f"отсутствует поле {i}")
                    
                event = create_event(
                    line_dict["timestamp"], 
                    line_dict["level"], 
                    line_dict["source"], 
                    line_dict["message"]
                )
            except json.JSONDecodeError:
                if not skip_invalid:
                    raise InvalidEventError(f"{file}, {index}: некорректный json")
                else: 
                    logging.warning(f"{file}, {index}: некорректный json")
                    yield None
                    continue
            except InvalidEventError as error:
                if not skip_invalid:            
                    raise InvalidEventError(f"{file}, {index}: {error}")
                else:
                    logging.warning(f"{file}, {index}: {error}")
                    yield None
                    continue
            except InvalidTimestampError as error:
                if not skip_invalid:
                    raise InvalidTimestampError(f"{file}, {index}: {error}")
                else:
                    logging.warning(f"{file}, {index}: {error}")
                    yield None
                    continue
            
            yield event


def parse_csv(file: str, skip_invalid: bool = False) -> Iterator[dict | None]:
    with open(file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        while True:
            try:
                row = next(reader)
                index = reader.line_num
                for i in FIELDS:
                    if i not in row:
                        raise InvalidEventError(f"отсутствует поле {i}")
                event = create_event(
                    row["timestamp"], 
                    row["level"], 
                    row["source"], 
                    row["message"]
                )
            except StopIteration:
                break
            except csv.Error:
                index = reader.reader.line_num
                if not skip_invalid:
                    raise InvalidEventError(f"{file}, {index}: некорректный csv")
                else:
                    logging.warning(f"{file}, {index}: некорректный csv")
                    yield None
                    continue
            except InvalidEventError as error:
                if not skip_invalid:
                    raise InvalidEventError(f"{file}, {index}: {error}")
                else:
                    logging.warning(f"{file}, {index}: {error}")
                    yield None
                    continue
            except InvalidTimestampError as error:
                if not skip_invalid:
                    raise InvalidTimestampError(f"{file}, {index}: {error}")
                else:
                    logging.warning(f"{file}, {index}: {error}")
                    yield None
                    continue
            yield event