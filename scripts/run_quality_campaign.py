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

from runner.config import load_benchmark_config, validate_document  # noqa: E402
from runner.discovery import discover_tasks, filter_tasks  # noqa: E402
from runner.execution import run_one_shot, run_repair  # noqa: E402
from runner.gpu_preflight import load_gpu_plan  # noqa: E402

RESUMABLE_STATUSES = {"running", "interrupted", "stopped"}
PARTIAL_RESULT_STATUSES = RESUMABLE_STATUSES | {"completed_with_failures", "failed"}


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _campaign_input_fingerprint(
    *,
    root: Path,
    private_tests_root: Path,
    tasks: list[Any],
    config_path: Path,
    plan_path: Path,
    seed: int | None,
) -> tuple[str, int]:
    """Fingerprint all code and task inputs that can affect this campaign."""
    files: dict[str, str] = {}

    def add_file(path: Path, label: str) -> None:
        if path.is_file() and not path.is_symlink():
            files[label] = _sha256(path)

    def add_tree(directory: Path, label: str, suffix: str | None = None) -> None:
        if not directory.is_dir():
            return
        for path in sorted(directory.rglob("*")):
            if (
                path.is_file()
                and not path.is_symlink()
                and not any(part in {".git", "__pycache__", ".pytest_cache"} for part in path.parts)
                and (suffix is None or path.suffix == suffix)
            ):
                files[f"{label}/{path.relative_to(directory).as_posix()}"] = _sha256(path)

    add_file(config_path, f"repo/{config_path.name}")
    add_file(plan_path, f"plan/{plan_path.name}")
    runtime_root = Path(__file__).resolve().parents[1]
    add_tree(runtime_root / "runner", "runtime/runner", ".py")
    add_tree(runtime_root / "schemas", "runtime/schemas", ".json")
    add_tree(runtime_root / "scripts", "runtime/scripts", ".py")
    add_file(runtime_root / "pyproject.toml", "runtime/pyproject.toml")
    for task in tasks:
        task_root = task.directory
        try:
            task_label = task_root.relative_to(root).as_posix()
        except ValueError:
            task_label = f"external-task/{task.id}"
        add_tree(task_root, task_label)
        private_root = private_tests_root / task.id
        add_tree(private_root, f"repo/private-tests/{task.id}")
    serialized = json.dumps(
        {"files": files, "seed": seed}, ensure_ascii=False, sort_keys=True
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest(), len(files)


def _relative_or_name(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


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
    error_items = (
        [item for item in errors if isinstance(item, dict)] if isinstance(errors, list) else []
    )
    error = (
        "; ".join(f"{item.get('type', 'error')}: {item.get('message', '')}" for item in error_items)
        or None
    )
    error_types = sorted({item.get("type", "error") for item in error_items})
    messages = " ".join(str(item.get("message", "")) for item in error_items).lower()
    outcome = validation.get("outcome", "not_run")
    capacity_markers = (
        "maximum context",
        "max context",
        "context length",
        "context window",
        "max_model_len",
        "max_position_embeddings",
        "prompt is too long",
        "input is too long",
        "token limit",
        "too many tokens",
        "sequence length",
        "max_context_bytes",
    )
    if outcome == "passed":
        failure_class = "passed"
    elif any(marker in messages for marker in capacity_markers) or (
        "ContextCapacityError" in error_types
    ):
        failure_class = "capacity_rejection"
    elif any(name in error_types for name in ("ChangeProtocolError", "ChangeApplicationError")):
        failure_class = "protocol_failure"
    elif any(
        name in error_types
        for name in ("ModelClientError", "TimeoutError", "ConnectionError", "URLError")
    ):
        failure_class = "infrastructure_failure"
    elif outcome in {"failed", "public_passed"}:
        failure_class = "functional_failure"
    else:
        failure_class = "execution_failure"
    return {
        "task_id": task_id,
        "status": run_metadata.get("status", "failed"),
        "validation_outcome": outcome,
        "failure_class": failure_class,
        "result_path": result_path,
        "error": error,
        "error_types": error_types,
    }


def _campaign_matches(
    campaign: dict[str, Any],
    *,
    campaign_id: str,
    mode: str,
    suite: str | None,
    category: str | None,
    config_path: Path,
    config_sha256: str,
    plan_path: Path,
    plan_sha256: str,
    comparison_type: str,
    comparison_group: str,
    artifact_variant: str,
    git_commit: str | None,
    input_fingerprint_sha256: str,
    seed: int | None,
    task_revisions: dict[str, int],
    task_ids: list[str],
) -> bool:
    if (
        campaign.get("id") != campaign_id
        or campaign.get("mode") != mode
        or campaign.get("suite") != suite
        or campaign.get("category") != category
        or campaign.get("config_path") != config_path.relative_to(config_path.parent).as_posix()
        or campaign.get("config_sha256") != config_sha256
        or campaign.get("plan_path") != _relative_or_name(config_path.parent, plan_path)
        or campaign.get("plan_sha256") != plan_sha256
        or campaign.get("comparison_type") != comparison_type
        or campaign.get("comparison_group") != comparison_group
        or campaign.get("artifact_variant") != artifact_variant
        or campaign.get("git_commit") != git_commit
        or campaign.get("input_fingerprint_sha256") != input_fingerprint_sha256
        or campaign.get("seed") != seed
    ):
        return False
    saved_task_ids = campaign.get("task_ids")
    return (saved_task_ids is None or saved_task_ids == task_ids) and campaign.get(
        "task_revisions"
    ) == task_revisions


def _find_resume_source(
    root: Path,
    *,
    campaign_id: str,
    mode: str,
    suite: str | None,
    category: str | None,
    config_path: Path,
    config_sha256: str,
    plan_path: Path,
    plan_sha256: str,
    comparison_type: str,
    comparison_group: str,
    artifact_variant: str,
    git_commit: str | None,
    input_fingerprint_sha256: str,
    seed: int | None,
    task_revisions: dict[str, int],
    task_ids: list[str],
) -> tuple[Path, dict[str, Any]] | None:
    campaigns_root = root / "results" / "raw" / "campaigns"
    if not campaigns_root.is_dir():
        return None

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
                parent_campaign.get("resumed_from") if isinstance(parent_campaign, dict) else None
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
            plan_path=plan_path,
            plan_sha256=plan_sha256,
            comparison_type=comparison_type,
            comparison_group=comparison_group,
            artifact_variant=artifact_variant,
            git_commit=git_commit,
            input_fingerprint_sha256=input_fingerprint_sha256,
            seed=seed,
            task_revisions=task_revisions,
            task_ids=task_ids,
        ):
            continue
        candidates.append((path.stat().st_mtime, path, snapshot))

    if not candidates:
        return None
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
    plan_path: Path,
    plan_sha256: str,
    comparison_type: str,
    comparison_group: str,
    artifact_variant: str,
    artifact_revision: str | None,
    git_commit: str | None,
    input_fingerprint_sha256: str,
    input_file_count: int,
    seed: int | None,
    task_revisions: dict[str, int],
    task_ids: list[str],
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "id": campaign_id,
        "mode": mode,
        "suite": suite,
        "category": category,
        "config_path": config_path.relative_to(config_path.parent).as_posix(),
        "config_sha256": config_sha256,
        "plan_path": _relative_or_name(config_path.parent, plan_path),
        "plan_sha256": plan_sha256,
        "comparison_type": comparison_type,
        "comparison_group": comparison_group,
        "artifact_variant": artifact_variant,
        "artifact_revision": artifact_revision,
        "git_commit": git_commit,
        "input_fingerprint_sha256": input_fingerprint_sha256,
        "input_file_count": input_file_count,
        "seed": seed,
        "task_revisions": task_revisions,
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
    classifications = [run.get("failure_class", "execution_failure") for run in runs]
    class_counts = {
        name: classifications.count(name)
        for name in (
            "functional_failure",
            "protocol_failure",
            "capacity_rejection",
            "infrastructure_failure",
            "execution_failure",
        )
    }
    quality_evaluated = (
        tasks_passed + class_counts["functional_failure"] + class_counts["protocol_failure"]
    )
    tasks_with_errors = sum(bool(run.get("error_types")) or bool(run.get("error")) for run in runs)
    return {
        "schema_version": "1.1",
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
            "tasks_functional_failures": class_counts["functional_failure"],
            "tasks_protocol_failures": class_counts["protocol_failure"],
            "tasks_capacity_rejections": class_counts["capacity_rejection"],
            "tasks_infrastructure_failures": class_counts["infrastructure_failure"],
            "tasks_execution_failures": class_counts["execution_failure"],
            "tasks_quality_evaluated": quality_evaluated,
            "quality_success_rate": tasks_passed / quality_evaluated if quality_evaluated else None,
            "error_counts": _error_counts(runs),
        },
    }


def _error_counts(runs: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for run in runs:
        error_types = run.get("error_types", [])
        if not isinstance(error_types, list):
            error_types = []
        if not error_types and run.get("error"):
            error_types = ["unknown"]
        for error_type in error_types:
            if isinstance(error_type, str):
                counts[error_type] = counts.get(error_type, 0) + 1
    return dict(sorted(counts.items()))


def _valid_resumed_runs(
    root: Path, runs: list[Any], tasks: list[Any], mode: str
) -> list[dict[str, Any]]:
    """Retain only completed entries backed by an existing matching raw result."""
    expected_revisions = {task.id: task.data["revision"] for task in tasks}
    valid: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in runs:
        if not isinstance(entry, dict):
            continue
        task_id = entry.get("task_id")
        result_path = entry.get("result_path")
        if (
            not isinstance(task_id, str)
            or task_id not in expected_revisions
            or task_id in seen
            or not isinstance(result_path, str)
            or not result_path
        ):
            continue
        candidate = (root / result_path).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            continue
        if not candidate.is_file():
            continue
        try:
            result = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        task = result.get("task", {})
        run = result.get("run", {})
        if (
            not isinstance(task, dict)
            or task.get("id") != task_id
            or task.get("revision") != expected_revisions[task_id]
            or not isinstance(run, dict)
            or run.get("mode") != mode
        ):
            continue
        seen.add(task_id)
        valid.append(entry)
    return valid


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
    parser.add_argument("--seed", type=int, help="override the configured generation seed")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--stop-on-error", action="store_true")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="resume the latest incomplete compatible run of this campaign",
    )
    options = parser.parse_args(arguments)
    config_path = options.config.resolve()
    plan_path = options.plan.resolve()
    plan = load_gpu_plan(plan_path)
    if options.campaign_id not in {item["id"] for item in plan["campaigns"]}:
        parser.error(f"campaign id is not present in {options.plan}: {options.campaign_id}")
    selected_plan = next(item for item in plan["campaigns"] if item["id"] == options.campaign_id)
    artifact = next(
        item
        for item in plan["model"]["artifact_variants"]
        if item["id"] == selected_plan["artifact_variant"]
    )
    config = load_benchmark_config(config_path)
    if options.seed is not None:
        config.data["model"]["generation"]["seed"] = options.seed
    effective_seed = config.data["model"]["generation"].get("seed")
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
    plan_sha256 = _sha256(plan_path)
    input_fingerprint_sha256, input_file_count = _campaign_input_fingerprint(
        root=config.root,
        private_tests_root=config.repository_path("private_tests"),
        tasks=tasks,
        config_path=config_path,
        plan_path=plan_path,
        seed=effective_seed,
    )
    git_commit = _git_commit(config.root)
    campaign_metadata = _campaign_metadata(
        campaign_id=options.campaign_id,
        mode=options.mode,
        suite=options.suite,
        category=options.category,
        config_path=config_path,
        config_sha256=config_sha256,
        plan_path=plan_path,
        plan_sha256=plan_sha256,
        comparison_type=selected_plan["comparison_type"],
        comparison_group=selected_plan["comparison_group"],
        artifact_variant=selected_plan["artifact_variant"],
        artifact_revision=artifact.get("revision"),
        git_commit=git_commit,
        input_fingerprint_sha256=input_fingerprint_sha256,
        input_file_count=input_file_count,
        seed=effective_seed,
        task_revisions={task.id: task.data["revision"] for task in tasks},
        task_ids=task_ids,
    )

    source_path: Path | None = None
    source_snapshot: dict[str, Any] | None = None
    if options.resume:
        source = _find_resume_source(
            config.root,
            campaign_id=options.campaign_id,
            mode=options.mode,
            suite=options.suite,
            category=options.category,
            config_path=config_path,
            config_sha256=config_sha256,
            plan_path=plan_path,
            plan_sha256=plan_sha256,
            comparison_type=selected_plan["comparison_type"],
            comparison_group=selected_plan["comparison_group"],
            artifact_variant=selected_plan["artifact_variant"],
            git_commit=git_commit,
            input_fingerprint_sha256=input_fingerprint_sha256,
            seed=effective_seed,
            task_revisions={task.id: task.data["revision"] for task in tasks},
            task_ids=task_ids,
        )
        if source is None:
            parser.error(
                "no incomplete campaign with a matching input fingerprint found; use the same "
                "commit, plan, config, runner, tasks, validators, seed and task selection"
            )
        source_path, source_snapshot = source
        source_runs = source_snapshot.get("runs", [])
        if not isinstance(source_runs, list):
            parser.error(f"invalid resume source (runs is not an array): {source_path}")
        runs = _valid_resumed_runs(config.root, source_runs, tasks, options.mode)
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
                campaign_run = _campaign_run_entry(result)
                if campaign_run is None:
                    raise ValueError(f"invalid run result for {task.id}")
                campaign_run["result_path"] = relative
                runs.append(campaign_run)
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
                        "failure_class": "execution_failure",
                        "result_path": "",
                        "error": f"{type(exc).__name__}: {exc}",
                        "error_types": [type(exc).__name__],
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
