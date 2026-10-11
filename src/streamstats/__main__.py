import argparse
import sys
from pathlib import Path
from collections.abc import Iterator

from streamstats.analysis import analyse_events
from streamstats.errors import CLIConfigError, StreamStatsError, UnsupportedFormatError
from streamstats.parsers import parse_csv, parse_jsonl
from streamstats.report import to_json


def read_events(files: list[str], parse_file, skip_invalid: bool) -> Iterator[dict | None]:
    """Последовательно выдаёт события из нескольких файлов с помощью выбранного парсера"""
    for file in files:
        yield from parse_file(file, skip_invalid)

   
def main() -> None:
    """Разбирает аргументы командной строки, запускает анализ и сохраняет отчёт"""
    parser = argparse.ArgumentParser(description="Потоковый анализатор файлов")
    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("files", nargs="+")
    analyze_parser.add_argument("--format", required=True)
    analyze_parser.add_argument("--output", default="report.json")
    analyze_parser.add_argument("--skip-invalid", action="store_true")
    args = parser.parse_args()
    
    try:
        output_path = Path(args.output).resolve()
        for input_file in args.files:
            input_path = Path(input_file).resolve()
            if output_path == input_path:
                raise CLIConfigError("Входной файл и файл отчета совпадают")
            
        if args.format == "csv":
            parse_file = parse_csv
        elif args.format == "jsonl":
            parse_file = parse_jsonl
        else:
            raise UnsupportedFormatError(f"Неподдерживаемый формат: {args.format}")
        events = read_events(args.files, parse_file, args.skip_invalid)
        statistics = analyse_events(events)
        to_json(args.output, statistics)
    except StreamStatsError as error:
        print(error, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()