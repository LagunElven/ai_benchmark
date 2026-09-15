from __future__ import annotations

import hashlib
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
from runner.workspace import CleanWorkspace, ValidatorWorkspace


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


def _record_model_response(
    result: dict[str, Any], store: ResultStore, response: Any, iteration: int | None = None
) -> str:
    raw_response = json.dumps(response.raw, ensure_ascii=False, indent=2, sort_keys=True)
    filename = "model-response.json" if iteration is None else f"model-response-{iteration}.json"
    artifact = store.write_artifact(filename, raw_response + "\n")
    result["artifacts"]["model_response"] = artifact
    result["artifacts"]["model_responses"].append(artifact)
    return artifact


def _accumulate_usage(result: dict[str, Any], response: Any) -> None:
    for key in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_tokens"):
        value = response.usage.get(key)
        current = result["usage"][key]
        if value is not None:
            result["usage"][key] = value if current is None else current + value
    current_generation = result["timing"]["generation_seconds"]
    result["timing"]["generation_seconds"] = (
        response.generation_seconds
        if current_generation is None
        else current_generation + response.generation_seconds
    )
    if result["timing"]["ttft_seconds"] is None and response.ttft_seconds is not None:
        result["timing"]["ttft_seconds"] = response.ttft_seconds


def _tokens_used(result: dict[str, Any]) -> int | None:
    input_tokens = result["usage"]["input_tokens"]
    output_tokens = result["usage"]["output_tokens"]
    if input_tokens is None or output_tokens is None:
        return None
    return input_tokens + output_tokens


def _set_repair_pass_metrics(
    result: dict[str, Any], max_iterations: int, successful_iteration: int | None
) -> None:
    for count in (1, 2, 3):
        key = f"pass_at_{count}"
        result["repair"][key] = (
            None
            if max_iterations < count
            else successful_iteration is not None and successful_iteration <= count
        )


def _failure_signature(results: list[CommandResult]) -> str:
    comparable = [
        {
            "name": result.name,
            "exit_code": result.exit_code,
            "timed_out": result.timed_out,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
        for result in results
    ]
    return hashlib.sha256(
        json.dumps(comparable, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _repair_feedback(iteration: int, feedback: str) -> str:
    return (
        f"# Public validation feedback after iteration {iteration}\n\n"
        "The previous change set did not pass public validation. Fix the current workspace. "
        "Only the public validator output below is available; hidden tests and hidden logs "
        "must not be inferred or requested. Return only the file_changes_v1 JSON object.\n\n"
        f"{feedback}"
    )


def _write_run_log(
    result: dict[str, Any], store: ResultStore, run_id: str, task: TaskDefinition, mode: str
) -> None:
    log_lines = [
        f"run_id: {run_id}",
        f"task_id: {task.id}",
        f"mode: {mode}",
        f"status: {result['run']['status']}",
        f"validation_outcome: {result['validation']['outcome']}",
        f"started_at: {result['timing']['started_at']}",
        f"ended_at: {result['timing']['ended_at']}",
    ]
    for error in result["errors"]:
        log_lines.append(f"error[{error['stage']}]: {error['type']}: {error['message']}")
    result["artifacts"]["run_log"] = store.write_artifact("run.log", "\n".join(log_lines) + "\n")


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
            "iterations": [],
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
            "model_responses": [],
            "validation_logs": [],
        },
        "errors": [],
    }


def _validation_group(
    specifications: list[dict[str, Any]],
    workspace: Path,
    timeout: int,
    store: ResultStore,
    artifact_prefix: str,
) -> tuple[dict[str, Any], list[str], str, str]:
    results: list[CommandResult] = []
    logs: list[str] = []
    for index, specification in enumerate(specifications, start=1):
        result = run_validator(specification, workspace, timeout)
        log_path = store.write_artifact(
            f"validation-{artifact_prefix}-{index}.log", format_log(result)
        )
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
    group = {
        "status": status,
        "passed": passed,
        "total": len(specifications),
        "commands": [result.summary(log) for result, log in zip(results, logs, strict=True)],
    }
    feedback = "\n\n".join(format_log(result) for result in results)
    if len(feedback) > 100_000:
        feedback = feedback[:100_000] + "\n[public feedback truncated]"
    return group, logs, _failure_signature(results), feedback


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
            _record_model_response(result, store, response)
            _accumulate_usage(result, response)

            apply_file_changes(response.content, workspace)
            result["patch"] = calculate_patch_metrics(
                baseline,
                workspace,
                task.data["workspace"].get("expected_modified_files"),
            ).as_dict()
            public, logs, _, _ = _validation_group(
                task.data["validation"]["public"],
                workspace,
                task.data["runtime"]["timeout_seconds"],
                store,
                "public",
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
                with ValidatorWorkspace(config, task, workspace, run_id) as validator_workspace:
                    hidden, hidden_logs, _, _ = _validation_group(
                        task.data["validation"]["hidden"],
                        validator_workspace,
                        task.data["runtime"]["timeout_seconds"],
                        store,
                        "hidden",
                    )
                result["validation"]["hidden"] = hidden
                result["artifacts"]["validation_logs"].extend(hidden_logs)
                hidden_passed = hidden["status"] == "passed"
                result["validation"]["outcome"] = "passed" if hidden_passed else "failed"
                result["validation"]["task_success"] = hidden_passed
                result["run"]["status"] = "completed"
                result["repair"]["pass_at_1"] = hidden_passed
                if hidden_passed:
                    result["repair"]["successful_iteration"] = 1
                    result["timing"]["time_until_success_seconds"] = time.monotonic() - started
                    tokens = result["usage"]["input_tokens"], result["usage"]["output_tokens"]
                    if all(value is not None for value in tokens):
                        result["usage"]["tokens_until_success"] = sum(tokens)  # type: ignore[arg-type]
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
        if task.has_hidden_validation and result["validation"]["public"]["status"] == "passed":
            result["validation"]["hidden"] = {
                "status": "failed",
                "passed": 0,
                "total": len(task.data["validation"]["hidden"]),
                "commands": [],
            }
        result["run"]["status"] = "failed"
        result["validation"]["outcome"] = "failed"
        result["validation"]["task_success"] = False
        result["repair"]["pass_at_1"] = False
    finally:
        result["timing"]["ended_at"] = _utc_now()
        result["timing"]["total_seconds"] = time.monotonic() - started

    _write_run_log(result, store, run_id, task, "one-shot")
    return store.save_result(result)


def run_repair(
    config: BenchmarkConfig,
    task: TaskDefinition,
    client: ModelClient | None = None,
) -> Path:
    """Run the bounded public-feedback repair loop and then hidden validation once."""
    if "repair" not in task.data["modes"]:
        raise BenchmarkError(f"Task {task.id} does not support repair mode")

    run_id = _run_id(task.id)
    store = ResultStore(config, run_id)
    store.create()
    started_at = _utc_now()
    started = time.monotonic()
    result = _base_result(config, task, run_id, started_at)
    result["run"]["mode"] = "repair"
    max_iterations = min(
        task.data["runtime"]["max_iterations"],
        config.data["runner"]["max_repair_iterations"],
    )
    max_output_tokens = task.data["runtime"]["max_output_tokens"]
    max_total_output_tokens = config.data["runner"]["max_repair_total_output_tokens"]
    max_total_seconds = config.data["runner"]["max_repair_total_seconds"]
    requested_output_tokens = 0
    feedback = ""
    failure_signatures: list[str] = []
    successful_iteration: int | None = None
    fatal_error = False

    try:
        with CleanWorkspace(config, task, run_id) as workspace:
            baseline = snapshot_files(workspace)
            model_client = client or create_client(config)
            for iteration in range(1, max_iterations + 1):
                if time.monotonic() - started >= max_total_seconds:
                    result["errors"].append(
                        {
                            "stage": "repair_budget",
                            "type": "TimeoutError",
                            "message": "Repair total time budget exhausted",
                        }
                    )
                    break
                remaining_output_tokens = max_total_output_tokens - requested_output_tokens
                if remaining_output_tokens <= 0:
                    result["errors"].append(
                        {
                            "stage": "repair_budget",
                            "type": "TokenBudgetError",
                            "message": "Repair total output token budget exhausted",
                        }
                    )
                    break

                messages = build_messages(
                    task, workspace, config.data["runner"]["max_context_bytes"]
                )
                if feedback:
                    messages.append(
                        {"role": "user", "content": _repair_feedback(iteration - 1, feedback)}
                    )
                call_max_output_tokens = min(max_output_tokens, remaining_output_tokens)
                requested_output_tokens += call_max_output_tokens
                attempt_started = time.monotonic()
                response_artifact: str | None = None
                result["usage"]["model_calls"] += 1
                try:
                    response = model_client.complete(
                        messages, max_output_tokens=call_max_output_tokens
                    )
                    response_artifact = _record_model_response(result, store, response, iteration)
                    _accumulate_usage(result, response)
                    apply_file_changes(response.content, workspace)
                except Exception as exc:
                    fatal_error = True
                    message = str(exc)
                    result["errors"].append(
                        {
                            "stage": f"repair_iteration_{iteration}",
                            "type": type(exc).__name__,
                            "message": message,
                        }
                    )
                    result["repair"]["iterations"].append(
                        {
                            "iteration": iteration,
                            "status": "error",
                            "duration_seconds": time.monotonic() - attempt_started,
                            "model_response": response_artifact,
                            "public": _empty_group(),
                            "error": message,
                        }
                    )
                    break

                result["patch"] = calculate_patch_metrics(
                    baseline,
                    workspace,
                    task.data["workspace"].get("expected_modified_files"),
                ).as_dict()
                try:
                    public, logs, signature, feedback = _validation_group(
                        task.data["validation"]["public"],
                        workspace,
                        task.data["runtime"]["timeout_seconds"],
                        store,
                        f"public-{iteration}",
                    )
                except Exception as exc:
                    fatal_error = True
                    message = str(exc)
                    result["errors"].append(
                        {
                            "stage": f"repair_iteration_{iteration}",
                            "type": type(exc).__name__,
                            "message": message,
                        }
                    )
                    result["repair"]["iterations"].append(
                        {
                            "iteration": iteration,
                            "status": "error",
                            "duration_seconds": time.monotonic() - attempt_started,
                            "model_response": response_artifact,
                            "public": _empty_group(),
                            "error": message,
                        }
                    )
                    break

                result["validation"]["public"] = public
                result["artifacts"]["validation_logs"].extend(logs)
                public_passed = public["status"] == "passed"
                result["validation"]["build_success"] = public_passed
                iteration_status = "public_passed" if public_passed else "public_failed"
                result["repair"]["iterations"].append(
                    {
                        "iteration": iteration,
                        "status": iteration_status,
                        "duration_seconds": time.monotonic() - attempt_started,
                        "model_response": response_artifact,
                        "public": public,
                        "error": None,
                    }
                )
                if not public_passed:
                    failure_signatures.append(signature)
                    continue

                if task.has_hidden_validation:
                    try:
                        with ValidatorWorkspace(
                            config, task, workspace, run_id
                        ) as validator_workspace:
                            hidden, hidden_logs, _, _ = _validation_group(
                                task.data["validation"]["hidden"],
                                validator_workspace,
                                task.data["runtime"]["timeout_seconds"],
                                store,
                                f"hidden-{iteration}",
                            )
                    except Exception as exc:
                        fatal_error = True
                        message = str(exc)
                        result["errors"].append(
                            {
                                "stage": f"hidden_validation_{iteration}",
                                "type": type(exc).__name__,
                                "message": message,
                            }
                        )
                        result["validation"]["hidden"] = {
                            "status": "failed",
                            "passed": 0,
                            "total": len(task.data["validation"]["hidden"]),
                            "commands": [],
                        }
                        result["repair"]["iterations"][-1]["status"] = "error"
                        result["repair"]["iterations"][-1]["error"] = message
                        break
                    result["validation"]["hidden"] = hidden
                    result["artifacts"]["validation_logs"].extend(hidden_logs)
                    if hidden["status"] != "passed":
                        result["repair"]["iterations"][-1]["status"] = "hidden_failed"
                        break

                successful_iteration = iteration
                result["repair"]["iterations"][-1]["status"] = "passed"
                result["validation"]["outcome"] = "passed"
                result["validation"]["task_success"] = True
                result["run"]["status"] = "completed"
                result["timing"]["time_until_success_seconds"] = time.monotonic() - started
                result["usage"]["tokens_until_success"] = _tokens_used(result)
                break
    except Exception as exc:
        fatal_error = True
        result["errors"].append(
            {"stage": "execution", "type": type(exc).__name__, "message": str(exc)}
        )
        result["validation"]["outcome"] = "failed"
        result["validation"]["task_success"] = False
    finally:
        if successful_iteration is None:
            result["validation"]["outcome"] = "failed"
            result["validation"]["task_success"] = False
            result["run"]["status"] = "failed" if fatal_error else "completed"
        result["repair"]["successful_iteration"] = successful_iteration
        _set_repair_pass_metrics(result, max_iterations, successful_iteration)
        if len(failure_signatures) >= 2:
            result["repair"]["repeated_failure_pattern"] = any(
                left == right
                for left, right in zip(failure_signatures, failure_signatures[1:], strict=False)
            )
        result["run"]["repair_iterations"] = len(result["repair"]["iterations"])
        result["timing"]["ended_at"] = _utc_now()
        result["timing"]["total_seconds"] = time.monotonic() - started

    _write_run_log(result, store, run_id, task, "repair")
    return store.save_result(result)
