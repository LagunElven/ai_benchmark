from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runner.config import BenchmarkConfig, load_structured_file, validate_document
from runner.errors import DiscoveryError


@dataclass(frozen=True)
class TaskDefinition:
    path: Path
    data: dict[str, Any]

    @property
    def directory(self) -> Path:
        return self.path.parent

    @property
    def id(self) -> str:
        return str(self.data["id"])

    @property
    def prompt_path(self) -> Path:
        return self.directory / "prompt.md"

    @property
    def has_hidden_validation(self) -> bool:
        return bool(self.data["validation"]["hidden"])


def discover_tasks(config: BenchmarkConfig) -> list[TaskDefinition]:
    tasks_root = config.repository_path("tasks")
    if not tasks_root.exists():
        return []
    schema_path = config.schema_dir / "task.schema.json"
    tasks: list[TaskDefinition] = []
    seen: dict[str, Path] = {}
    for path in sorted(tasks_root.rglob("task.yaml")):
        data = load_structured_file(path)
        validate_document(data, schema_path, path)
        task = TaskDefinition(path=path, data=data)
        if task.id in seen:
            raise DiscoveryError(f"Duplicate task id {task.id}: {seen[task.id]} and {path}")
        if not task.prompt_path.is_file():
            raise DiscoveryError(f"Task {task.id} is missing prompt.md")
        seen[task.id] = path
        tasks.append(task)
    return tasks


def filter_tasks(
    tasks: Iterable[TaskDefinition],
    *,
    suite: str | None = None,
    tag: str | None = None,
    category: str | None = None,
) -> list[TaskDefinition]:
    return [
        task
        for task in tasks
        if (suite is None or suite in task.data["suites"])
        and (tag is None or tag in task.data["tags"])
        and (category is None or category == task.data["category"])
    ]


def find_task(tasks: Iterable[TaskDefinition], task_id: str) -> TaskDefinition:
    matches = [task for task in tasks if task.id == task_id]
    if not matches:
        raise DiscoveryError(f"Unknown task id: {task_id}")
    return matches[0]
