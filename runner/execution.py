from __future__ import annotations

import importlib.metadata
import json
import platform
import subprocess
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from runner.changes import apply_file_changes
from runner.client import ModelClient, create_client
from runner.config import BenchmarkConfig
from runner.diffing import PatchMetrics, calculate_patch_metrics, snapshot_files
from runner.discovery import TaskDefinition
from runner.errors import BenchmarkError
from runner.prompting import build_messages
from runner.results import ResultStore
from runner.validation import CommandResult, format_log, run_validator
from runner.workspace import CleanWorkspace


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _run_id(task_id: str) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    return f"{stamp}-{task_id.lower()}-{uuid.uuid4().hex[:8]}"


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


def _package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _empty_group() -> dict[str, Any]:
    return {"status": "not_run", "passed": 0, "total": 0, "commands": []}


def _empty_patch() -> dict[str, Any]:
    return PatchMetrics([], [], [], 0, 0, None, None).as_dict()


def _base_result(
    config: BenchmarkConfig, task: TaskDefinition, run_id: str, started_at: str
) -> dict[str, Any]:
    model = config.data["model"]
    generation = model["generation"]
    return {
        "schema_version": "1.0",
        "benchmark": {
            "name": config.data["benchmark"]["name"],
            "version": config.data["benchmark"]["version"],
            "git_commit": _git_commit(config.root),
        },
        "run": {
            "id": run_id,
            "timestamp": started_at,
            "mode": "one-shot",
            "status": "failed",
            "repair_iterations": 0,
        },
        "task": {
            "id": task.id,
            "revision": task.data["revision"],
            "category": task.data["category"],
            "suites": task.data["suites"],
        },
        "model": {
            "provider": model["provider"],
            "name": model["name"],
            "revision": model.get("revision"),
            "tokenizer_revision": model.get("tokenizer_revision"),
            "quantization": model.get("quantization"),
            "dtype": model.get("dtype"),
            "parameters": generation,
        },
        "environment": {
            "hardware": {
                **config.data["hardware"],
                "machine": platform.machine(),
                "detected_processor": platform.processor(),
            },
            "software": {
                "os": platform.platform(),
                "python": platform.python_version(),
                "pyyaml": _package_version("PyYAML"),
                "jsonschema": _package_version("jsonschema"),
            },
            "serving": {
                **config.data["serving"],
                "base_url": model.get("base_url"),
            },
        },
        "timing": {
            "started_at": started_at,
            "ended_at": started_at,
            "total_seconds": 0.0,
            "ttft_seconds": None,
            "generation_seconds": None,
            "time_until_success_seconds": None,
        },
        "usage": {
            "input_tokens": None,
            "cached_input_tokens": None,
            "output_tokens": None,
            "reasoning_tokens": None,
            "tokens_until_success": None,
            "model_calls": 0,
        },
        "repair": {
            "pass_at_1": None,
            "pass_at_2": None,
            "pass_at_3": None,
            "successful_iteration": None,
            "repeated_failure_pattern": None,
        },
        "validation": {
            "outcome": "not_run",
            "task_success": None,
            "build_success": None,
            "public": _empty_group(),
            "hidden": _empty_group(),
            "regression": _empty_group(),
        },
        "patch": _empty_patch(),
        "artifacts": {
            "result": "",
            "run_log": None,
            "model_response": None,
            "validation_logs": [],
        },
        "errors": [],
    }


def _validation_group(
    specifications: list[dict[str, Any]],
    workspace: Path,
    timeout: int,
    store: ResultStore,
) -> tuple[dict[str, Any], list[str]]:
    results: list[CommandResult] = []
    logs: list[str] = []
    for index, specification in enumerate(specifications, start=1):
        result = run_validator(specification, workspace, timeout)
        log_path = store.write_artifact(f"validation-public-{index}.log", format_log(result))
        logs.append(log_path)
        results.append(result)
        if not result.passed:
            break
    passed = sum(result.passed for result in results)
    status = (
        "passed" if len(results) == len(specifications) and passed == len(results) else "failed"
    )
    if not specifications:
        status = "passed"
    return {
        "status": status,
        "passed": passed,
        "total": len(specifications),
        "commands": [result.summary(log) for result, log in zip(results, logs, strict=True)],
    }, logs


def run_one_shot(
    config: BenchmarkConfig,
    task: TaskDefinition,
    client: ModelClient | None = None,
) -> Path:
    if "one-shot" not in task.data["modes"]:
        raise BenchmarkError(f"Task {task.id} does not support one-shot mode")
    run_id = _run_id(task.id)
    store = ResultStore(config, run_id)
    store.create()
    started_at = _utc_now()
    started = time.monotonic()
    result = _base_result(config, task, run_id, started_at)
    try:
        with CleanWorkspace(config, task, run_id) as workspace:
            baseline = snapshot_files(workspace)
            messages = build_messages(task, workspace, config.data["runner"]["max_context_bytes"])
            model_client = client or create_client(config)
            result["usage"]["model_calls"] = 1
            response = model_client.complete(
                messages, max_output_tokens=task.data["runtime"]["max_output_tokens"]
            )
            result["timing"]["generation_seconds"] = response.generation_seconds
            result["timing"]["ttft_seconds"] = response.ttft_seconds
            result["usage"].update(response.usage)
            raw_response = json.dumps(response.raw, ensure_ascii=False, indent=2, sort_keys=True)
            result["artifacts"]["model_response"] = store.write_artifact(
                "model-response.json", raw_response + "\n"
            )

            apply_file_changes(response.content, workspace)
            result["patch"] = calculate_patch_metrics(
                baseline,
                workspace,
                task.data["workspace"].get("expected_modified_files"),
            ).as_dict()
            public, logs = _validation_group(
                task.data["validation"]["public"],
                workspace,
                task.data["runtime"]["timeout_seconds"],
                store,
            )
            result["validation"]["public"] = public
            result["artifacts"]["validation_logs"] = logs
            public_passed = public["status"] == "passed"
            result["validation"]["build_success"] = public_passed

            if not public_passed:
                result["validation"]["outcome"] = "failed"
                result["validation"]["task_success"] = False
                result["run"]["status"] = "completed"
                result["repair"]["pass_at_1"] = False
            elif task.has_hidden_validation:
                result["validation"]["outcome"] = "public_passed"
                result["validation"]["task_success"] = None
                result["run"]["status"] = "incomplete"
            else:
                result["validation"]["outcome"] = "passed"
                result["validation"]["task_success"] = True
                result["run"]["status"] = "completed"
                result["repair"]["pass_at_1"] = True
                result["repair"]["successful_iteration"] = 1
                result["timing"]["time_until_success_seconds"] = time.monotonic() - started
                tokens = result["usage"]["input_tokens"], result["usage"]["output_tokens"]
                if all(value is not None for value in tokens):
                    result["usage"]["tokens_until_success"] = sum(tokens)  # type: ignore[arg-type]
    except Exception as exc:
        result["errors"].append(
            {"stage": "execution", "type": type(exc).__name__, "message": str(exc)}
        )
        result["run"]["status"] = "failed"
        result["validation"]["outcome"] = "failed"
        result["validation"]["task_success"] = False
        result["repair"]["pass_at_1"] = False
    finally:
        result["timing"]["ended_at"] = _utc_now()
        result["timing"]["total_seconds"] = time.monotonic() - started

    log_lines = [
        f"run_id: {run_id}",
        f"task_id: {task.id}",
        "mode: one-shot",
        f"status: {result['run']['status']}",
        f"validation_outcome: {result['validation']['outcome']}",
        f"started_at: {result['timing']['started_at']}",
        f"ended_at: {result['timing']['ended_at']}",
    ]
    for error in result["errors"]:
        log_lines.append(f"error[{error['stage']}]: {error['type']}: {error['message']}")
    result["artifacts"]["run_log"] = store.write_artifact("run.log", "\n".join(log_lines) + "\n")
    return store.save_result(result)
