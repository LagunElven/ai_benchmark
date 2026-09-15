from __future__ import annotations

import argparse
import json
import sys

from runner.config import load_benchmark_config
from runner.discovery import discover_tasks, filter_tasks, find_task
from runner.errors import BenchmarkError
from runner.execution import run_one_shot, run_repair


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="enterprise-llm-bench")
    parser.add_argument("--config", default="benchmark.yaml", help="benchmark configuration")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("validate-config", help="validate benchmark configuration")

    list_parser = commands.add_parser("list-tasks", help="discover and list benchmark tasks")
    list_parser.add_argument("--suite")
    list_parser.add_argument("--tag")
    list_parser.add_argument("--category")
    list_parser.add_argument("--json", action="store_true", dest="as_json")

    run_parser = commands.add_parser("run", help="execute one benchmark task")
    run_parser.add_argument("--task-id", required=True)
    run_parser.add_argument("--mode", choices=["one-shot", "repair"], default="one-shot")
    return parser


def main(arguments: list[str] | None = None) -> int:
    parser = _parser()
    options = parser.parse_args(arguments)
    try:
        config = load_benchmark_config(options.config)
        if options.command == "validate-config":
            print(f"valid: {config.path}")
            return 0

        tasks = discover_tasks(config)
        if options.command == "list-tasks":
            selected = filter_tasks(
                tasks, suite=options.suite, tag=options.tag, category=options.category
            )
            if options.as_json:
                print(
                    json.dumps(
                        [
                            {
                                "id": task.id,
                                "revision": task.data["revision"],
                                "name": task.data["name"],
                                "category": task.data["category"],
                                "suites": task.data["suites"],
                                "tags": task.data["tags"],
                            }
                            for task in selected
                        ],
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            else:
                for task in selected:
                    print(
                        f"{task.id}\trev={task.data['revision']}\t"
                        f"{task.data['category']}\t{task.data['name']}"
                    )
            return 0

        if options.command == "run":
            task = find_task(tasks, options.task_id)
            result_path = (
                run_one_shot(config, task)
                if options.mode == "one-shot"
                else run_repair(config, task)
            )
            print(result_path)
            return 0
        parser.error(f"Unknown command: {options.command}")
    except BenchmarkError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
