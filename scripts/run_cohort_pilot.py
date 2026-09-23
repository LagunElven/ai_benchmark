"""Run a finite, closed-loop cohort of model-assisted benchmark tasks."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import subprocess
import sys
import threading
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from runner.cohort import CohortRun, run_closed_cohort  # noqa: E402
from runner.config import (  # noqa: E402
    BenchmarkConfig,
    load_benchmark_config,
    load_structured_file,
    validate_document,
)
from runner.discovery import TaskDefinition, discover_tasks  # noqa: E402
from runner.errors import ConfigurationError  # noqa: E402

DEFAULT_PLAN = REPOSITORY_ROOT / "campaigns" / "cohort" / "qwen3.8-agentic-pilot.yaml"


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_state(root: Path) -> tuple[str | None, bool | None]:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout
        return commit or None, bool(status.strip())
    except (OSError, subprocess.SubprocessError):
        return None, None


def _relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ConfigurationError(f"Path must remain inside the repository: {path}") from exc


def _nearest_rank(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, int(len(ordered) * percentile + 0.999999))
    return ordered[rank - 1]


def _sum_known(values: list[Any]) -> int | None:
    known = [int(value) for value in values if isinstance(value, (int, float))]
    return sum(known) if known else None


def _load_plan(path: Path, config: BenchmarkConfig) -> dict[str, Any]:
    plan_path = path.resolve()
    _relative(config.root, plan_path)
    plan = load_structured_file(plan_path)
    validate_document(
        plan,
        config.schema_dir / "cohort-pilot-config.schema.json",
        plan_path,
    )
    return plan


def _select_tasks(plan: dict[str, Any], config: BenchmarkConfig) -> list[TaskDefinition]:
    discovered = {task.id: task for task in discover_tasks(config)}
    selected: list[TaskDefinition] = []
    missing: list[str] = []
    for task_id in plan["tasks"]:
        task = discovered.get(task_id)
        if task is None:
            missing.append(task_id)
            continue
        if plan["mode"] not in task.data["modes"]:
            raise ConfigurationError(f"Task {task_id} does not support mode {plan['mode']}")
        selected.append(task)
    if missing:
        raise ConfigurationError(f"Unknown tasks in cohort plan: {', '.join(missing)}")
    oversized = [agents for agents in plan["agent_counts"] if agents > len(selected)]
    if oversized:
        raise ConfigurationError(
            f"Configured agent counts cannot exceed the {len(selected)} distinct pilot tasks: "
            f"{oversized}"
        )
    return selected


def _maximum_agent_count(task_count: int, max_num_seqs: int | None) -> int:
    limits = [task_count]
    if max_num_seqs is not None:
        limits.append(max_num_seqs)
    return min(limits)


def _validate_agent_count(
    agents: int,
    *,
    task_count: int,
    max_num_seqs: int | None,
) -> None:
    if agents < 1:
        raise ConfigurationError("--agents must be at least 1")
    if agents > task_count:
        raise ConfigurationError(
            f"--agents ({agents}) exceeds the number of distinct pilot tasks ({task_count})"
        )
    if max_num_seqs is not None and agents > max_num_seqs:
        raise ConfigurationError(
            f"--agents ({agents}) exceeds serving.max_num_seqs ({max_num_seqs})"
        )


def _summary(result: CohortRun) -> dict[str, Any]:
    tasks = result.tasks
    total = len(tasks)
    completed = sum(task["result_path"] is not None for task in tasks)
    succeeded = sum(task["task_success"] is True for task in tasks)
    capacity_rejected = sum("ContextCapacityError" in task["error_types"] for task in tasks)
    runner_errors = sum(
        task["result_path"] is None
        or (
            task["run_status"] == "failed"
            and "ContextCapacityError" not in task["error_types"]
        )
        for task in tasks
    )
    quality_evaluated = max(0, completed - capacity_rejected - runner_errors)
    request_seconds = sum(
        request["duration_seconds"] or 0.0 for request in result.model_requests
    )
    elapsed = result.elapsed_seconds
    durations = [float(task["duration_seconds"]) for task in tasks]
    model_calls = len(result.model_requests)
    return {
        "tasks_total": total,
        "tasks_completed": completed,
        "tasks_succeeded": succeeded,
        "tasks_failed": total - succeeded,
        "tasks_quality_evaluated": quality_evaluated,
        "tasks_capacity_rejected": capacity_rejected,
        "tasks_runner_errors": runner_errors,
        "task_success_rate": succeeded / quality_evaluated if quality_evaluated else None,
        "tasks_per_hour": total / elapsed * 3600 if elapsed > 0 else 0.0,
        "successful_tasks_per_hour": succeeded / elapsed * 3600 if elapsed > 0 else 0.0,
        "task_duration_p50_seconds": _nearest_rank(durations, 0.50),
        "task_duration_p95_seconds": _nearest_rank(durations, 0.95),
        "total_model_calls": model_calls,
        "completed_model_requests": sum(
            request["status"] == "completed" for request in result.model_requests
        ),
        "failed_model_requests": sum(
            request["status"] == "failed" for request in result.model_requests
        ),
        "total_input_tokens": _sum_known([r["input_tokens"] for r in result.model_requests]),
        "total_output_tokens": _sum_known([r["output_tokens"] for r in result.model_requests]),
        "total_reasoning_tokens": _sum_known(
            [r["reasoning_tokens"] for r in result.model_requests]
        ),
        "total_model_request_seconds": request_seconds,
        "average_active_model_requests": request_seconds / elapsed if elapsed > 0 else 0.0,
        "max_concurrent_model_requests": result.max_concurrent_model_requests,
        "max_active_agents": result.max_active_agents,
    }


def _campaign_document(
    *,
    config: BenchmarkConfig,
    plan: dict[str, Any],
    plan_path: Path,
    benchmark_config_path: Path,
    tasks: list[TaskDefinition],
    agents: int,
    started_at: str,
    ended_at: str,
    result: CohortRun,
    git_commit: str | None,
    working_tree_dirty: bool | None,
) -> dict[str, Any]:
    campaign_id = (
        f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%S.%fZ')}-cohort-"
        f"a{agents}-{uuid.uuid4().hex[:8]}"
    )
    summary = _summary(result)
    config_data = config.data
    errors = summary["tasks_failed"] > 0
    return {
        "schema_version": "1.0",
        "benchmark": {
            "name": config_data["benchmark"]["name"],
            "version": config_data["benchmark"]["version"],
            "git_commit": git_commit,
            "working_tree_dirty": working_tree_dirty,
        },
        "campaign": {
            "id": campaign_id,
            "status": "completed_with_failures" if errors else "completed",
            "comparison_type": "operational_solution",
            "comparison_group": plan["name"],
            "workload_name": plan["name"],
            "workload_version": plan["version"],
            "workload_model": "closed_loop_finite_cohort",
            "mode": plan["mode"],
            "agent_count": agents,
            "configured_agent_counts": plan["agent_counts"],
            "task_ids": [task.id for task in tasks],
            "task_revisions": {task.id: task.data["revision"] for task in tasks},
            "seed": config_data["model"]["generation"].get("seed"),
            "started_at": started_at,
            "ended_at": ended_at,
            "benchmark_config_path": _relative(config.root, benchmark_config_path),
            "benchmark_config_sha256": _sha256(benchmark_config_path),
            "cohort_plan_path": _relative(config.root, plan_path),
            "cohort_plan_sha256": _sha256(plan_path),
        },
        "model": {
            key: config_data["model"].get(key)
            for key in (
                "provider",
                "name",
                "source_repository",
                "revision",
                "tokenizer_revision",
                "quantization",
                "dtype",
            )
        }
        | {"generation": copy.deepcopy(config_data["model"]["generation"])},
        "environment": {
            "hardware_declared": copy.deepcopy(config_data["hardware"]),
            "serving": {
                "engine": config_data["serving"].get("engine"),
                "engine_version": config_data["serving"].get("engine_version"),
                "endpoint": config_data["model"].get("base_url"),
                "launch_command": config_data["serving"].get("launch_command"),
                "agent_concurrency": agents,
                "max_num_seqs": config_data["serving"].get("max_num_seqs"),
                "max_model_length": config_data["serving"].get("max_model_length"),
                "tensor_parallel_size": config_data["serving"].get("tensor_parallel_size"),
                "pipeline_parallel_size": config_data["serving"].get("pipeline_parallel_size"),
                "reasoning_parser": config_data["serving"].get("reasoning_parser"),
                "prefix_caching": config_data["serving"].get("prefix_caching"),
                "kv_cache_dtype": config_data["serving"].get("kv_cache_dtype"),
            },
            "runner": {"platform": platform.platform(), "python_version": sys.version.split()[0]},
            "resource_metrics_source": "not_sampled; remote GPU metrics unavailable",
        },
        "timing": {
            "started_at": started_at,
            "ended_at": ended_at,
            "total_seconds": result.elapsed_seconds,
        },
        "summary": summary,
        "tasks": result.tasks,
        "model_requests": result.model_requests,
    }


def _persist_campaign(config: BenchmarkConfig, campaign: dict[str, Any]) -> Path:
    raw_root = config.repository_path("results") / "raw"
    campaign_root = raw_root / "cohort"
    run_directory = campaign_root / campaign["campaign"]["id"]
    run_directory.mkdir(parents=True, exist_ok=False)
    result_path = run_directory / "campaign.json"
    validate_document(campaign, config.schema_dir / "cohort-pilot-result.schema.json", result_path)
    serialized = json.dumps(campaign, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with result_path.open("x", encoding="utf-8", newline="") as stream:
        stream.write(serialized)
    campaign_root.mkdir(parents=True, exist_ok=True)
    index_path = campaign_root / "campaigns.jsonl"
    descriptor = os.open(index_path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
    try:
        line = json.dumps(campaign, ensure_ascii=False, sort_keys=True) + "\n"
        os.write(descriptor, line.encode("utf-8"))
    finally:
        os.close(descriptor)
    return result_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark-config", type=Path, required=True)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument(
        "--agents",
        type=int,
        help="number of cohort agents (1..min(task count, serving.max_num_seqs))",
    )
    parser.add_argument("--plan-only", action="store_true")
    options = parser.parse_args(argv)

    try:
        benchmark_config_path = options.benchmark_config.resolve()
        config = load_benchmark_config(benchmark_config_path)
        plan_path = options.plan.resolve()
        if not options.plan.is_absolute():
            plan_path = (config.root / options.plan).resolve()
        plan = _load_plan(plan_path, config)
        tasks = _select_tasks(plan, config)
    except (ConfigurationError, OSError, ValueError) as exc:
        parser.error(str(exc))

    if options.plan_only:
        max_num_seqs = config.data["serving"].get("max_num_seqs")
        print(
            json.dumps(
                {
                    "benchmark_config": _relative(config.root, benchmark_config_path),
                    "cohort_plan": _relative(config.root, plan_path),
                    "mode": plan["mode"],
                    "agent_counts": plan["agent_counts"],
                    "maximum_supported_agent_count": _maximum_agent_count(
                        len(tasks), max_num_seqs
                    ),
                    "task_count": len(tasks),
                    "task_ids": [task.id for task in tasks],
                    "workload_model": "closed_loop_finite_cohort",
                    "task_order": (
                        "FIFO; each agent takes the next task after finishing its current task"
                    ),
                    "model_server_contacted": False,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if options.agents is None:
        parser.error("--agents is required unless --plan-only is used")
    max_num_seqs = config.data["serving"].get("max_num_seqs")
    try:
        _validate_agent_count(
            options.agents,
            task_count=len(tasks),
            max_num_seqs=max_num_seqs,
        )
    except ConfigurationError as exc:
        parser.error(str(exc))

    started_at = _utc_now()
    started = time.monotonic()
    effective_data = copy.deepcopy(config.data)
    effective_data["serving"]["concurrency"] = options.agents
    effective_config = BenchmarkConfig(config.root, config.path, effective_data)
    print(
        f"Starting closed-loop cohort: {options.agents} agents, {len(tasks)} tasks, "
        f"mode={plan['mode']}",
        flush=True,
    )
    progress_lock = threading.Lock()
    completed_count = 0

    def report_task_completion(task: dict[str, Any]) -> None:
        nonlocal completed_count
        with progress_lock:
            completed_count += 1
            outcome = task["validation_outcome"]
            print(
                f"[{completed_count}/{len(tasks)}] {task['task_id']} "
                f"(agent {task['agent_id']}): {outcome}",
                flush=True,
            )

    try:
        result = run_closed_cohort(
            effective_config,
            tasks,
            agents=options.agents,
            mode=plan["mode"],
            started=started,
            on_task_complete=report_task_completion,
        )
    except KeyboardInterrupt:
        print("Cohort interrupted; completed task runs remain in results/raw/.", file=sys.stderr)
        return 130
    ended_at = _utc_now()
    git_commit, working_tree_dirty = _git_state(config.root)
    campaign = _campaign_document(
        config=effective_config,
        plan=plan,
        plan_path=plan_path,
        benchmark_config_path=benchmark_config_path,
        tasks=tasks,
        agents=options.agents,
        started_at=started_at,
        ended_at=ended_at,
        result=result,
        git_commit=git_commit,
        working_tree_dirty=working_tree_dirty,
    )
    result_path = _persist_campaign(config, campaign)
    print(
        json.dumps(
            {
                "status": campaign["campaign"]["status"],
                "campaign": _relative(config.root, result_path),
                "tasks_succeeded": campaign["summary"]["tasks_succeeded"],
                "tasks_total": campaign["summary"]["tasks_total"],
                "total_seconds": round(campaign["timing"]["total_seconds"], 2),
                "max_concurrent_model_requests": campaign["summary"][
                    "max_concurrent_model_requests"
                ],
            },
            ensure_ascii=False,
        ),
        flush=True,
    )
    return 0 if campaign["summary"]["tasks_succeeded"] == campaign["summary"]["tasks_total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
