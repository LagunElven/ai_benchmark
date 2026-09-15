from __future__ import annotations

import shutil
from pathlib import Path

from runner.config import BenchmarkConfig
from runner.discovery import TaskDefinition
from runner.errors import WorkspaceError


def _ensure_inside(root: Path, candidate: Path, label: str) -> Path:
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise WorkspaceError(f"{label} resolves outside {root}: {candidate}") from exc
    return resolved


def _reject_symlinks(source: Path) -> None:
    for entry in source.rglob("*"):
        if entry.is_symlink():
            raise WorkspaceError(f"Workspace sources may not contain symlinks: {entry}")


def _copy_includes(task_root: Path, workspace: Path, includes: list[dict[str, str]]) -> None:
    for include in includes:
        source = _ensure_inside(
            task_root, task_root / include["source"], "workspace.include source"
        )
        if not source.exists():
            raise WorkspaceError(f"Included workspace source does not exist: {source}")
        if source.is_symlink():
            raise WorkspaceError(f"Included workspace source may not be a symlink: {source}")
        if source.is_dir():
            _reject_symlinks(source)
        target = _ensure_inside(
            workspace, workspace / include["target"], "workspace.include target"
        )
        if target.exists():
            raise WorkspaceError(f"Included workspace target already exists: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


class CleanWorkspace:
    def __init__(self, config: BenchmarkConfig, task: TaskDefinition, run_id: str) -> None:
        self.config = config
        self.task = task
        self.run_id = run_id
        self.path: Path | None = None

    def __enter__(self) -> Path:
        task_root = self.task.directory.resolve()
        source = _ensure_inside(
            task_root,
            task_root / self.task.data["workspace"]["source"],
            "workspace.source",
        )
        if not source.is_dir():
            raise WorkspaceError(f"Workspace source does not exist for {self.task.id}: {source}")
        _reject_symlinks(source)

        work_root = self.config.repository_path("work")
        work_root.mkdir(parents=True, exist_ok=True)
        destination = _ensure_inside(work_root, work_root / self.run_id, "run workspace")
        if destination.exists():
            raise WorkspaceError(f"Run workspace already exists: {destination}")
        shutil.copytree(source, destination)
        _copy_includes(task_root, destination, self.task.data["workspace"].get("include", []))
        self.path = destination
        return destination

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self.path is None or self.config.data["runner"]["keep_workspaces"]:
            return
        work_root = self.config.repository_path("work").resolve()
        target = self.path.resolve()
        try:
            target.relative_to(work_root)
        except ValueError as safety_error:
            raise WorkspaceError(
                f"Refusing to remove workspace outside {work_root}"
            ) from safety_error
        shutil.rmtree(target)
