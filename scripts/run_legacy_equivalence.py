"""Run executable Java migrations for the legacy fixture catalogue."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from runner.client import FakeModelClient  # noqa: E402
from runner.config import load_benchmark_config  # noqa: E402
from runner.discovery import discover_tasks, filter_tasks  # noqa: E402
from runner.execution import run_one_shot  # noqa: E402


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="benchmark.yaml")
    parser.add_argument("--task-id", action="append")
    options = parser.parse_args(arguments)
    config_path = Path(options.config)
    if not config_path.is_absolute():
        config_path = REPOSITORY_ROOT / config_path
    config = load_benchmark_config(config_path)
    tasks = filter_tasks(discover_tasks(config), category="cobol")
    tasks += filter_tasks(discover_tasks(config), category="delphi")
    tasks += filter_tasks(discover_tasks(config), category="windev")
    tasks += filter_tasks(discover_tasks(config), category="abal")
    if options.task_id:
        wanted = set(options.task_id)
        tasks = [task for task in tasks if task.id in wanted]
        missing = wanted - {task.id for task in tasks}
        if missing:
            parser.error(f"unknown legacy task: {', '.join(sorted(missing))}")

    fixture_root = REPOSITORY_ROOT / "tests" / "fixtures"
    failures = 0
    for task in tasks:
        fixture = fixture_root / "legacy-responses" / f"{task.id}.json"
        if not fixture.is_file():
            fixture = fixture_root / "smoke-responses" / f"{task.id}.json"
        if not fixture.is_file():
            print(f"{task.id}: missing response fixture", file=sys.stderr)
            failures += 1
            continue
        result_path = run_one_shot(
            config, task, FakeModelClient(fixture.read_text(encoding="utf-8"))
        )
        result = json.loads(result_path.read_text(encoding="utf-8"))
        status = result["validation"]["outcome"]
        print(f"{task.id}: {status} ({result_path.as_posix()})")
        failures += status != "passed"
    print(f"legacy equivalence summary: {len(tasks) - failures}/{len(tasks)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
