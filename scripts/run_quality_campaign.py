"""Run a reproducible quality campaign and persist an append-only campaign index."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from runner.config import load_benchmark_config, validate_document  # noqa: E402
from runner.discovery import discover_tasks, filter_tasks  # noqa: E402
from runner.execution import run_one_shot, run_repair  # noqa: E402
from runner.gpu_preflight import load_gpu_plan  # noqa: E402


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit(root: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return completed.stdout.strip() or None


def _write_campaign_result(root: Path, result: dict[str, Any]) -> Path:
    output_root = root / "results" / "raw" / "campaigns"
    output_root.mkdir(parents=True, exist_ok=True)
    run_id = (
        f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%S.%fZ')}-"
        f"{result['campaign']['id'].lower()}-{uuid.uuid4().hex[:8]}"
    )
    directory = output_root / run_id
    directory.mkdir()
    path = directory / "campaign.json"
    schema = root / "schemas" / "quality-campaign-result.schema.json"
    validate_document(result, schema, path)
    path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    index_path = output_root / "campaigns.jsonl"
    with index_path.open("a", encoding="utf-8", newline="") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-id", required=True, help="planned id, for example C-003")
    parser.add_argument("--config", type=Path, default=REPOSITORY_ROOT / "benchmark.yaml")
    parser.add_argument(
        "--plan", type=Path, default=REPOSITORY_ROOT / "campaigns" / "gpu" / "plan.yaml"
    )
    parser.add_argument("--mode", choices=["one-shot", "repair"], default="repair")
    parser.add_argument("--suite", default="full")
    parser.add_argument("--category")
    parser.add_argument("--task-id", action="append")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--stop-on-error", action="store_true")
    options = parser.parse_args(arguments)
    config_path = options.config.resolve()
    plan = load_gpu_plan(options.plan)
    if options.campaign_id not in {item["id"] for item in plan["campaigns"]}:
        parser.error(f"campaign id is not present in {options.plan}: {options.campaign_id}")
    config = load_benchmark_config(config_path)
    tasks = filter_tasks(discover_tasks(config), suite=options.suite, category=options.category)
    if options.task_id:
        requested = set(options.task_id)
        tasks = [task for task in tasks if task.id in requested]
        missing = requested - {task.id for task in tasks}
        if missing:
            parser.error(f"task is not selected by the filters: {', '.join(sorted(missing))}")
    if not tasks:
        parser.error("no task selected")
    if options.plan_only:
        print(json.dumps([task.id for task in tasks], ensure_ascii=False, indent=2))
        return 0

    started_at = _utc_now()
    runs: list[dict[str, Any]] = []
    tasks_passed = 0
    tasks_failed = 0
    tasks_with_errors = 0
    for index, task in enumerate(tasks, start=1):
        print(f"[{index}/{len(tasks)}] {task.id}", flush=True)
        try:
            result_path = (
                run_one_shot(config, task)
                if options.mode == "one-shot"
                else run_repair(config, task)
            )
            result = json.loads(result_path.read_text(encoding="utf-8"))
            validation_outcome = result["validation"]["outcome"]
            passed = validation_outcome == "passed"
            tasks_passed += passed
            tasks_failed += not passed
            tasks_with_errors += bool(result["errors"])
            relative = result_path.relative_to(config.root).as_posix()
            runs.append(
                {
                    "task_id": task.id,
                    "status": result["run"]["status"],
                    "validation_outcome": validation_outcome,
                    "result_path": relative,
                    "error": None,
                }
            )
            print(f"  {validation_outcome}: {relative}", flush=True)
            if options.stop_on_error and not passed:
                break
        except Exception as exc:  # Keep the campaign index useful after one bad task.
            tasks_failed += 1
            tasks_with_errors += 1
            runs.append(
                {
                    "task_id": task.id,
                    "status": "failed",
                    "validation_outcome": "not_run",
                    "result_path": "",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            print(f"  error: {exc}", file=sys.stderr, flush=True)
            if options.stop_on_error:
                break
    ended_at = _utc_now()
    result = {
        "schema_version": "1.0",
        "type": "quality_campaign_result",
        "campaign": {
            "id": options.campaign_id,
            "mode": options.mode,
            "suite": options.suite,
            "category": options.category,
            "config_path": config_path.relative_to(config.root).as_posix(),
            "config_sha256": _sha256(config_path),
            "git_commit": _git_commit(config.root),
        },
        "started_at": started_at,
        "ended_at": ended_at,
        "status": "completed" if tasks_failed == 0 else "completed_with_failures",
        "runs": runs,
        "summary": {
            "tasks_total": len(tasks),
            "tasks_passed": tasks_passed,
            "tasks_failed": tasks_failed,
            "tasks_with_errors": tasks_with_errors,
        },
    }
    result_path = _write_campaign_result(config.root, result)
    print(
        json.dumps(
            {"status": result["status"], "campaign": str(result_path)},
            ensure_ascii=False,
        )
    )
    return 0 if tasks_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
