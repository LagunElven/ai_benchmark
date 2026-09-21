"""Run a reproducible quality campaign and persist an append-only campaign index."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from runner.config import BenchmarkConfig, load_benchmark_config, validate_document  # noqa: E402
from runner.discovery import discover_tasks, filter_tasks  # noqa: E402
from runner.execution import run_one_shot, run_repair  # noqa: E402
from runner.gpu_preflight import load_gpu_plan  # noqa: E402

RESUMABLE_STATUSES = {"running", "interrupted", "stopped"}
PARTIAL_RESULT_STATUSES = RESUMABLE_STATUSES | {"completed_with_failures", "failed"}


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


def _campaign_run_id(campaign_id: str) -> str:
    return (
        f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%S.%fZ')}-"
        f"{campaign_id.lower()}-{uuid.uuid4().hex[:8]}"
    )


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            stream.write(serialized)
        temporary_path.replace(path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def _write_campaign_snapshot(root: Path, path: Path, result: dict[str, Any]) -> None:
    schema = root / "schemas" / "quality-campaign-result.schema.json"
    validate_document(result, schema, path)
    _write_json_atomic(path, result)


def _create_campaign_directory(root: Path, campaign_id: str) -> Path:
    output_root = root / "results" / "raw" / "campaigns"
    output_root.mkdir(parents=True, exist_ok=True)
    directory = output_root / _campaign_run_id(campaign_id)
    directory.mkdir()
    return directory


def _append_campaign_index(root: Path, result: dict[str, Any]) -> None:
    output_root = root / "results" / "raw" / "campaigns"
    output_root.mkdir(parents=True, exist_ok=True)
    index_path = output_root / "campaigns.jsonl"
    with index_path.open("a", encoding="utf-8", newline="") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")


def _read_campaign_snapshot(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _same_config_values(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    return all(value is None or actual.get(key) == value for key, value in expected.items())


def _run_matches_config(run: dict[str, Any], config: BenchmarkConfig) -> bool:
    benchmark = run.get("benchmark", {})
    model = run.get("model", {})
    environment = run.get("environment", {})
    if not isinstance(benchmark, dict) or not isinstance(model, dict):
        return False
    if benchmark.get("name") != config.data["benchmark"]["name"]:
        return False
    if benchmark.get("version") != config.data["benchmark"]["version"]:
        return False
    model_config = config.data["model"]
    model_keys = ("provider", "name", "revision", "tokenizer_revision", "quantization", "dtype")
    if any(model.get(key) != model_config.get(key) for key in model_keys):
        return False
    parameters = model.get("parameters", {})
    if not isinstance(parameters, dict):
        return False
    generation = {
        key: value
        for key, value in model_config["generation"].items()
        if key != "max_output_tokens"
    }
    if not _same_config_values(generation, parameters):
        return False
    return all(
        isinstance(environment.get(section), dict)
        and _same_config_values(values, environment[section])
        for section, values in (
            ("hardware", config.data["hardware"]),
            ("serving", config.data["serving"]),
        )
    )


def _campaign_run_entry(run: dict[str, Any]) -> dict[str, Any] | None:
    task = run.get("task", {})
    run_metadata = run.get("run", {})
    validation = run.get("validation", {})
    artifacts = run.get("artifacts", {})
    if not all(isinstance(value, dict) for value in (task, run_metadata, validation, artifacts)):
        return None
    result_path = artifacts.get("result")
    task_id = task.get("id")
    if not isinstance(result_path, str) or not isinstance(task_id, str):
        return None
    errors = run.get("errors", [])
    error = None
    if errors:
        error = "; ".join(
            f"{item.get('type', 'error')}: {item.get('message', '')}"
            for item in errors
            if isinstance(item, dict)
        )
    return {
        "task_id": task_id,
        "status": run_metadata.get("status", "failed"),
        "validation_outcome": validation.get("outcome", "not_run"),
        "result_path": result_path,
        "error": error,
    }


def _legacy_run_source(
    root: Path,
    *,
    config: BenchmarkConfig,
    campaign_id: str,
    mode: str,
    suite: str | None,
    category: str | None,
    config_path: Path,
    config_sha256: str,
    task_ids: list[str],
) -> tuple[Path, dict[str, Any]] | None:
    index_path = root / "results" / "raw" / "runs.jsonl"
    if not index_path.is_file() or not task_ids:
        return None

    entries: list[dict[str, Any]] = []
    try:
        lines = index_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines:
        try:
            run = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(run, dict):
            entries.append(run)

    candidates: list[tuple[int, list[dict[str, Any]]]] = []
    for start, run in enumerate(entries):
        if run.get("task", {}).get("id") != task_ids[0]:
            continue
        sequence: list[dict[str, Any]] = []
        for expected_id, candidate in zip(task_ids, entries[start:], strict=False):
            if (
                candidate.get("run", {}).get("mode") != mode
                or not _run_matches_config(candidate, config)
                or candidate.get("task", {}).get("id") != expected_id
            ):
                break
            campaign_run = _campaign_run_entry(candidate)
            if campaign_run is None:
                break
            sequence.append(campaign_run)
        if 0 < len(sequence) < len(task_ids):
            candidates.append((start, sequence))
    if not candidates:
        return None

    start, runs = max(candidates, key=lambda item: item[0])
    source = {
        "schema_version": "1.0",
        "type": "quality_campaign_result",
        "campaign": {
            "id": campaign_id,
            "mode": mode,
            "suite": suite,
            "category": category,
            "config_path": config_path.relative_to(config_path.parent).as_posix(),
            "config_sha256": config_sha256,
            "git_commit": _git_commit(root),
            "task_ids": task_ids,
        },
        "started_at": entries[start].get("timing", {}).get("started_at", _utc_now()),
        "ended_at": entries[start + len(runs) - 1]
        .get("timing", {})
        .get("ended_at", _utc_now()),
        "status": "interrupted",
        "runs": runs,
        "summary": {
            "tasks_total": len(task_ids),
            "tasks_passed": sum(item["validation_outcome"] == "passed" for item in runs),
            "tasks_failed": sum(item["validation_outcome"] != "passed" for item in runs),
            "tasks_with_errors": sum(bool(item["error"]) for item in runs),
        },
    }
    return index_path, source


def _campaign_matches(
    campaign: dict[str, Any],
    *,
    campaign_id: str,
    mode: str,
    suite: str | None,
    category: str | None,
    config_path: Path,
    config_sha256: str,
    task_ids: list[str],
) -> bool:
    if (
        campaign.get("id") != campaign_id
        or campaign.get("mode") != mode
        or campaign.get("suite") != suite
        or campaign.get("category") != category
        or campaign.get("config_path") != config_path.relative_to(config_path.parent).as_posix()
        or campaign.get("config_sha256") != config_sha256
    ):
        return False
    saved_task_ids = campaign.get("task_ids")
    return saved_task_ids is None or saved_task_ids == task_ids


def _find_resume_source(
    root: Path,
    *,
    config: BenchmarkConfig,
    campaign_id: str,
    mode: str,
    suite: str | None,
    category: str | None,
    config_path: Path,
    config_sha256: str,
    task_ids: list[str],
) -> tuple[Path, dict[str, Any]] | None:
    campaigns_root = root / "results" / "raw" / "campaigns"
    if not campaigns_root.is_dir():
        return _legacy_run_source(
            root,
            config=config,
            campaign_id=campaign_id,
            mode=mode,
            suite=suite,
            category=category,
            config_path=config_path,
            config_sha256=config_sha256,
            task_ids=task_ids,
        )

    snapshots: dict[Path, dict[str, Any]] = {}
    for directory in campaigns_root.iterdir():
        if not directory.is_dir():
            continue
        for filename in ("campaign-progress.json", "campaign.json"):
            path = directory / filename
            if path.is_file():
                snapshot = _read_campaign_snapshot(path)
                if snapshot is not None:
                    snapshots[path.resolve()] = snapshot

    superseded: set[Path] = set()
    for snapshot_path, snapshot in snapshots.items():
        campaign = snapshot.get("campaign")
        status = snapshot.get("status")
        runs = snapshot.get("runs", [])
        summary = snapshot.get("summary")
        if (
            not isinstance(campaign, dict)
            or not isinstance(runs, list)
            or not isinstance(summary, dict)
        ):
            continue
        expected_total = summary.get("tasks_total")
        if status not in {"completed", "completed_with_failures"} or not (
            isinstance(expected_total, int) and len(runs) >= expected_total
        ):
            continue
        progress_sibling = (snapshot_path.parent / "campaign-progress.json").resolve()
        if progress_sibling in snapshots:
            superseded.add(progress_sibling)
        source = campaign.get("resumed_from")
        visited: set[Path] = set()
        while isinstance(source, str) and source:
            source_path = (root / source).resolve()
            if source_path in visited:
                break
            visited.add(source_path)
            superseded.add(source_path)
            parent = snapshots.get(source_path, {})
            parent_campaign = parent.get("campaign")
            source = (
                parent_campaign.get("resumed_from")
                if isinstance(parent_campaign, dict)
                else None
            )

    candidates: list[tuple[float, Path, dict[str, Any]]] = []
    for path, snapshot in snapshots.items():
        if path in superseded:
            continue
        campaign = snapshot.get("campaign", {})
        runs = snapshot.get("runs", [])
        summary = snapshot.get("summary")
        if (
            not isinstance(campaign, dict)
            or not isinstance(runs, list)
            or not isinstance(summary, dict)
        ):
            continue
        status = snapshot.get("status")
        expected_total = summary.get("tasks_total")
        is_partial = isinstance(expected_total, int) and len(runs) < expected_total
        if campaign.get("task_ids") is None and expected_total != len(task_ids):
            continue
        if status in {"interrupted", "stopped"} and not is_partial:
            continue
        if status not in RESUMABLE_STATUSES and not (
            status in PARTIAL_RESULT_STATUSES and is_partial
        ):
            continue
        if not _campaign_matches(
            campaign,
            campaign_id=campaign_id,
            mode=mode,
            suite=suite,
            category=category,
            config_path=config_path,
            config_sha256=config_sha256,
            task_ids=task_ids,
        ):
            continue
        candidates.append((path.stat().st_mtime, path, snapshot))

    if not candidates:
        return _legacy_run_source(
            root,
            config=config,
            campaign_id=campaign_id,
            mode=mode,
            suite=suite,
            category=category,
            config_path=config_path,
            config_sha256=config_sha256,
            task_ids=task_ids,
        )
    _, path, snapshot = max(candidates, key=lambda item: item[0])
    return path, snapshot


def _campaign_metadata(
    *,
    campaign_id: str,
    mode: str,
    suite: str,
    category: str | None,
    config_path: Path,
    config_sha256: str,
    git_commit: str | None,
    task_ids: list[str],
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "id": campaign_id,
        "mode": mode,
        "suite": suite,
        "category": category,
        "config_path": config_path.relative_to(config_path.parent).as_posix(),
        "config_sha256": config_sha256,
        "git_commit": git_commit,
        "task_ids": task_ids,
    }
    return metadata


def _campaign_result(
    *,
    metadata: dict[str, Any],
    started_at: str,
    ended_at: str,
    status: str,
    runs: list[dict[str, Any]],
    tasks_total: int,
) -> dict[str, Any]:
    tasks_passed = sum(run["validation_outcome"] == "passed" for run in runs)
    tasks_failed = len(runs) - tasks_passed
    tasks_with_errors = sum(bool(run.get("error")) for run in runs)
    return {
        "schema_version": "1.0",
        "type": "quality_campaign_result",
        "campaign": metadata,
        "started_at": started_at,
        "ended_at": ended_at,
        "status": status,
        "runs": runs,
        "summary": {
            "tasks_total": tasks_total,
            "tasks_passed": tasks_passed,
            "tasks_failed": tasks_failed,
            "tasks_with_errors": tasks_with_errors,
        },
    }


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
    parser.add_argument(
        "--resume",
        action="store_true",
        help="resume the latest incomplete compatible run of this campaign",
    )
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

    task_ids = [task.id for task in tasks]
    config_sha256 = _sha256(config_path)
    campaign_metadata = _campaign_metadata(
        campaign_id=options.campaign_id,
        mode=options.mode,
        suite=options.suite,
        category=options.category,
        config_path=config_path,
        config_sha256=config_sha256,
        git_commit=_git_commit(config.root),
        task_ids=task_ids,
    )

    source_path: Path | None = None
    source_snapshot: dict[str, Any] | None = None
    if options.resume:
        source = _find_resume_source(
            config.root,
            config=config,
            campaign_id=options.campaign_id,
            mode=options.mode,
            suite=options.suite,
            category=options.category,
            config_path=config_path,
            config_sha256=config_sha256,
            task_ids=task_ids,
        )
        if source is None:
            parser.error(
                "no incomplete compatible campaign found; use the same campaign id, "
                "config, mode, suite, category and task selection"
            )
        source_path, source_snapshot = source
        source_runs = source_snapshot.get("runs", [])
        if not isinstance(source_runs, list):
            parser.error(f"invalid resume source (runs is not an array): {source_path}")
        runs = list(source_runs)
        campaign_metadata["resumed_from"] = source_path.relative_to(config.root).as_posix()
        started_at = source_snapshot.get("started_at", _utc_now())
        print(f"Resuming {source_path}", flush=True)
    else:
        runs = []
        started_at = _utc_now()

    completed_task_ids = {run.get("task_id") for run in runs if isinstance(run, dict)}
    pending_tasks = [task for task in tasks if task.id not in completed_task_ids]
    campaign_directory = _create_campaign_directory(config.root, options.campaign_id)
    progress_path = campaign_directory / "campaign-progress.json"
    progress = _campaign_result(
        metadata=campaign_metadata,
        started_at=started_at,
        ended_at=_utc_now(),
        status="running",
        runs=runs,
        tasks_total=len(tasks),
    )
    _write_campaign_snapshot(config.root, progress_path, progress)

    try:
        for index, task in enumerate(pending_tasks, start=1):
            completed_count = len(completed_task_ids) + index - 1
            print(f"[{completed_count + 1}/{len(tasks)}] {task.id}", flush=True)
            try:
                result_path = (
                    run_one_shot(config, task)
                    if options.mode == "one-shot"
                    else run_repair(config, task)
                )
                result = json.loads(result_path.read_text(encoding="utf-8"))
                validation_outcome = result["validation"]["outcome"]
                passed = validation_outcome == "passed"
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
                progress = _campaign_result(
                    metadata=campaign_metadata,
                    started_at=started_at,
                    ended_at=_utc_now(),
                    status="running",
                    runs=runs,
                    tasks_total=len(tasks),
                )
                _write_campaign_snapshot(config.root, progress_path, progress)
                if options.stop_on_error and not passed:
                    break
            except Exception as exc:  # Keep the campaign progress useful after one bad task.
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
                progress = _campaign_result(
                    metadata=campaign_metadata,
                    started_at=started_at,
                    ended_at=_utc_now(),
                    status="running",
                    runs=runs,
                    tasks_total=len(tasks),
                )
                _write_campaign_snapshot(config.root, progress_path, progress)
                if options.stop_on_error:
                    break
    except KeyboardInterrupt:
        interrupted = _campaign_result(
            metadata=campaign_metadata,
            started_at=started_at,
            ended_at=_utc_now(),
            status="interrupted",
            runs=runs,
            tasks_total=len(tasks),
        )
        _write_campaign_snapshot(config.root, progress_path, interrupted)
        print(
            json.dumps(
                {"status": "interrupted", "progress": str(progress_path)},
                ensure_ascii=False,
            ),
            file=sys.stderr,
        )
        return 130

    complete = len(runs) == len(tasks)
    if not complete:
        progress = _campaign_result(
            metadata=campaign_metadata,
            started_at=started_at,
            ended_at=_utc_now(),
            status="stopped",
            runs=runs,
            tasks_total=len(tasks),
        )
        _write_campaign_snapshot(config.root, progress_path, progress)
        print(
            json.dumps(
                {"status": "stopped", "progress": str(progress_path)},
                ensure_ascii=False,
            )
        )
        return 1

    tasks_failed = sum(run["validation_outcome"] != "passed" for run in runs)
    final_result = _campaign_result(
        metadata=campaign_metadata,
        started_at=started_at,
        ended_at=_utc_now(),
        status="completed" if tasks_failed == 0 else "completed_with_failures",
        runs=runs,
        tasks_total=len(tasks),
    )
    result_path = campaign_directory / "campaign.json"
    _write_campaign_snapshot(config.root, result_path, final_result)
    _append_campaign_index(config.root, final_result)
    _write_campaign_snapshot(
        config.root,
        progress_path,
        {**final_result, "status": "completed"},
    )
    print(
        json.dumps(
            {"status": final_result["status"], "campaign": str(result_path)},
            ensure_ascii=False,
        )
    )
    return 0 if tasks_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
