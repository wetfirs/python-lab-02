import json
import subprocess
import sys


def test_cli_multiple_files(tmp_path):
    first_file = tmp_path / "first.jsonl"
    second_file = tmp_path / "second.jsonl"
    report_file = tmp_path / "report.json"
    first_text = (
        '{"timestamp": "2026-10-08T10:00:00", "level": "INFO", "source": "app", "message": "сообщение"}\n'
    )
    second_text = (
        '{"timestamp": "2026-10-09T22:00:00", "level": "ERROR", "source": "app", "message": "сообщение"}\n'
    )

    first_file.write_text(first_text, encoding="utf-8")
    second_file.write_text(second_text, encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable, "-m", "streamstats", "analyze",
            str(first_file), str(second_file),
            "--format", "jsonl",
            "--output", str(report_file),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report_text = report_file.read_text(encoding="utf-8")
    report = json.loads(report_text)

    assert report["event_count"] == 2
    assert report["sources"] == {"app": 2}
    assert "app" in report_text

    assert first_file.read_text(encoding="utf-8") == first_text
    assert second_file.read_text(encoding="utf-8") == second_text


def test_cli_invalid_json(tmp_path):
    input_file = tmp_path / "events.jsonl"
    report_file = tmp_path / "report.json"
    input_file.write_text('{"timestamp":\n', encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable, "-m", "streamstats", "analyze",
            str(input_file),
            "--format", "jsonl",
            "--output", str(report_file),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert f"{input_file}, 1:" in result.stderr
    assert not report_file.exists()


def test_cli_skip_invalid(tmp_path):
    input_file = tmp_path / "events.jsonl"
    output_file = tmp_path / "report.json"
    input_file.write_text(
        '{"timestamp":\n'
        '{"timestamp": "2026-10-08T10:00:00", "level": "INFO", "source": "app", "message": "hello"}\n',
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable, "-m", "streamstats", "analyze",
            str(input_file),
            "--format", "jsonl",
            "--output", str(output_file),
            "--skip-invalid",
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    statistics = json.loads(output_file.read_text(encoding="utf-8"))
    assert statistics["event_count"] == 1
    assert statistics["skip_count"] == 1