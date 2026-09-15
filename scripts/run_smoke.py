"""Run the deterministic offline smoke suite with test-adapter responses.

The response fixtures live under tests/ and are never copied into a model
workspace. They are a harness for validating the runner and task packaging,
not benchmark results for a real model.
"""

# The repository root must be on sys.path when this file is invoked directly.
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from runner.client import FakeModelClient
from runner.config import load_benchmark_config
from runner.discovery import discover_tasks, filter_tasks
from runner.execution import run_one_shot, run_repair


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="benchmark.yaml")
    parser.add_argument("--mode", choices=["one-shot", "repair"], default="one-shot")
    parser.add_argument("--task-id", action="append")
    options = parser.parse_args(arguments)

    config_path = Path(options.config)
    if not config_path.is_absolute():
        config_path = REPOSITORY_ROOT / config_path
    config = load_benchmark_config(config_path)
    tasks = filter_tasks(discover_tasks(config), suite="smoke")
    if options.task_id:
        wanted = set(options.task_id)
        tasks = [task for task in tasks if task.id in wanted]
        missing = wanted - {task.id for task in tasks}
        if missing:
            parser.error(f"task is not in smoke suite: {', '.join(sorted(missing))}")

    fixture_root = config.root / "tests" / "fixtures" / "smoke-responses"
    failures = 0
    for task in tasks:
        fixture = fixture_root / f"{task.id}.json"
        if not fixture.is_file():
            print(f"{task.id}: missing adapter fixture {fixture}", file=sys.stderr)
            failures += 1
            continue
        client = FakeModelClient(fixture.read_text(encoding="utf-8"))
        result_path = (
            run_one_shot(config, task, client)
            if options.mode == "one-shot"
            else run_repair(config, task, client)
        )
        result = json.loads(result_path.read_text(encoding="utf-8"))
        status = result["validation"]["outcome"]
        print(f"{task.id}: {status} ({result_path.as_posix()})")
        failures += status != "passed"

    print(f"smoke summary: {len(tasks) - failures}/{len(tasks)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
