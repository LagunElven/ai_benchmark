"""Closed-loop cohorts of quality tasks for agentic workload pilots."""

from __future__ import annotations

import json
import queue
import threading
import time
from collections.abc import Callable, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from runner.client import ModelClient, create_client
from runner.config import BenchmarkConfig
from runner.discovery import TaskDefinition
from runner.execution import run_one_shot, run_repair


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True)
class CohortRun:
    tasks: list[dict[str, Any]]
    model_requests: list[dict[str, Any]]
    elapsed_seconds: float
    max_active_agents: int
    max_concurrent_model_requests: int


class TrackedModelClient:
    """Track model-call timing and concurrency without retaining prompts or outputs."""

    def __init__(self, client: ModelClient, started: float) -> None:
        self._client = client
        self._started = started
        self._lock = threading.Lock()
        self._local = threading.local()
        self._active = 0
        self._max_active = 0
        self._next_request_id = 0
        self._requests: list[dict[str, Any]] = []

    @contextmanager
    def task_context(self, *, task_id: str, agent_id: int) -> Iterator[None]:
        previous = getattr(self._local, "context", None)
        self._local.context = {"task_id": task_id, "agent_id": agent_id}
        try:
            yield
        finally:
            self._local.context = previous

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        max_output_tokens: int,
    ) -> Any:
        context = getattr(self._local, "context", {})
        started = time.monotonic()
        with self._lock:
            self._next_request_id += 1
            request_id = f"model-{self._next_request_id:04d}"
            self._active += 1
            self._max_active = max(self._max_active, self._active)
            request: dict[str, Any] = {
                "request_id": request_id,
                "task_id": context.get("task_id"),
                "agent_id": context.get("agent_id"),
                "started_offset_seconds": max(0.0, started - self._started),
                "ended_offset_seconds": None,
                "duration_seconds": None,
                "status": "running",
                "input_tokens": None,
                "output_tokens": None,
                "reasoning_tokens": None,
                "cached_input_tokens": None,
                "error_type": None,
            }
            self._requests.append(request)

        try:
            response = self._client.complete(messages, max_output_tokens=max_output_tokens)
        except Exception as exc:
            ended = time.monotonic()
            with self._lock:
                request.update(
                    {
                        "ended_offset_seconds": max(0.0, ended - self._started),
                        "duration_seconds": max(0.0, ended - started),
                        "status": "failed",
                        "error_type": type(exc).__name__,
                    }
                )
                self._active -= 1
            raise

        ended = time.monotonic()
        usage = response.usage or {}
        with self._lock:
            request.update(
                {
                    "ended_offset_seconds": max(0.0, ended - self._started),
                    "duration_seconds": max(0.0, ended - started),
                    "status": "completed",
                    "input_tokens": usage.get("input_tokens"),
                    "output_tokens": usage.get("output_tokens"),
                    "reasoning_tokens": usage.get("reasoning_tokens"),
                    "cached_input_tokens": usage.get("cached_input_tokens"),
                }
            )
            self._active -= 1
        return response

    def snapshot(self) -> tuple[list[dict[str, Any]], int]:
        with self._lock:
            return [dict(item) for item in self._requests], self._max_active


def run_closed_cohort(
    config: BenchmarkConfig,
    tasks: list[TaskDefinition],
    *,
    agents: int,
    mode: str,
    started: float | None = None,
    client: ModelClient | None = None,
    task_executor: Callable[[BenchmarkConfig, TaskDefinition, ModelClient, str], Path]
    | None = None,
    on_task_complete: Callable[[dict[str, Any]], None] | None = None,
) -> CohortRun:
    """Run a finite FIFO task queue; each agent takes its next task after completion."""
    if agents < 1:
        raise ValueError("agents must be at least 1")
    if agents > len(tasks):
        raise ValueError("agents cannot exceed the number of distinct tasks in the pilot")
    if mode not in {"one-shot", "repair"}:
        raise ValueError(f"unsupported task mode: {mode}")

    cohort_started = time.monotonic() if started is None else started
    tracked_client = TrackedModelClient(client or create_client(config), cohort_started)
    execute = task_executor or _execute_task
    work: queue.Queue[tuple[int, TaskDefinition] | None] = queue.Queue()
    for sequence, task in enumerate(tasks, start=1):
        work.put((sequence, task))
    for _ in range(agents):
        work.put(None)

    task_lock = threading.Lock()
    stop_workers = threading.Event()
    task_records: list[dict[str, Any]] = []
    active_agents = 0
    max_active_agents = 0

    def worker(agent_id: int) -> None:
        nonlocal active_agents, max_active_agents
        while True:
            if stop_workers.is_set():
                return
            item = work.get()
            if item is None:
                work.task_done()
                return
            if stop_workers.is_set():
                work.task_done()
                return
            sequence, task = item
            task_started = time.monotonic()
            task_started_at = _utc_now()
            with task_lock:
                active_agents += 1
                max_active_agents = max(max_active_agents, active_agents)
            result_path: Path | None = None
            result: dict[str, Any] | None = None
            error_type: str | None = None
            try:
                with tracked_client.task_context(task_id=task.id, agent_id=agent_id):
                    result_path = execute(config, task, tracked_client, mode)
                result = json.loads(result_path.read_text(encoding="utf-8"))
            except Exception as exc:  # Preserve the rest of the cohort after an isolated run error.
                error_type = type(exc).__name__
            finally:
                task_ended = time.monotonic()
                with task_lock:
                    active_agents -= 1
                    record: dict[str, Any] = {
                        "sequence": sequence,
                        "task_id": task.id,
                        "task_revision": task.data["revision"],
                        "agent_id": agent_id,
                        "started_at": task_started_at,
                        "ended_at": _utc_now(),
                        "started_offset_seconds": max(0.0, task_started - cohort_started),
                        "ended_offset_seconds": max(0.0, task_ended - cohort_started),
                        "duration_seconds": max(0.0, task_ended - task_started),
                        "run_status": None,
                        "validation_outcome": "not_run",
                        "task_success": None,
                        "model_calls": 0,
                        "input_tokens": None,
                        "output_tokens": None,
                        "reasoning_tokens": None,
                        "result_path": None,
                        "error_type": error_type,
                        "error_types": [],
                    }
                    if result is not None and result_path is not None:
                        error_types = [
                            str(error["type"])
                            for error in result.get("errors", [])
                            if isinstance(error, dict) and error.get("type")
                        ]
                        record.update(
                            {
                                "run_status": result.get("run", {}).get("status"),
                                "validation_outcome": result.get("validation", {}).get(
                                    "outcome", "not_run"
                                ),
                                "task_success": result.get("validation", {}).get(
                                    "task_success"
                                ),
                                "model_calls": result.get("usage", {}).get("model_calls", 0),
                                "input_tokens": result.get("usage", {}).get("input_tokens"),
                                "output_tokens": result.get("usage", {}).get("output_tokens"),
                                "reasoning_tokens": result.get("usage", {}).get(
                                    "reasoning_tokens"
                                ),
                                "result_path": result_path.relative_to(config.root).as_posix(),
                                "error_types": error_types,
                            }
                        )
                    elif error_type is not None:
                        record["error_types"] = [error_type]
                    task_records.append(record)
                if on_task_complete is not None:
                    on_task_complete(dict(record))
                work.task_done()

    executor = ThreadPoolExecutor(max_workers=agents, thread_name_prefix="cohort-agent")
    futures = [executor.submit(worker, agent_id) for agent_id in range(1, agents + 1)]
    try:
        for future in as_completed(futures):
            future.result()
    except BaseException:
        stop_workers.set()
        executor.shutdown(wait=True, cancel_futures=True)
        raise
    else:
        executor.shutdown(wait=True)

    elapsed = max(0.0, time.monotonic() - cohort_started)
    requests, max_model_requests = tracked_client.snapshot()
    return CohortRun(
        tasks=sorted(task_records, key=lambda item: item["sequence"]),
        model_requests=requests,
        elapsed_seconds=elapsed,
        max_active_agents=max_active_agents,
        max_concurrent_model_requests=max_model_requests,
    )


def _execute_task(
    config: BenchmarkConfig,
    task: TaskDefinition,
    client: ModelClient,
    mode: str,
) -> Path:
    if mode == "one-shot":
        return run_one_shot(config, task, client)
    return run_repair(config, task, client)
