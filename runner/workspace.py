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


def _copy_overlay(source: Path, destination: Path) -> None:
    """Copy a trusted validator-only tree without replacing model files."""
    if not source.is_dir():
        raise WorkspaceError(f"Hidden test source is not a directory: {source}")
    _reject_symlinks(source)
    for source_entry in sorted(source.rglob("*")):
        relative = source_entry.relative_to(source)
        target_entry = _ensure_inside(
            destination, destination / relative, "hidden test destination"
        )
        if source_entry.is_dir():
            if target_entry.exists() and not target_entry.is_dir():
                raise WorkspaceError(
                    f"Hidden test path collides with a model file: {relative.as_posix()}"
                )
            target_entry.mkdir(parents=True, exist_ok=True)
            continue
        if target_entry.exists():
            raise WorkspaceError(
                f"Hidden test path collides with a model file: {relative.as_posix()}"
            )
        target_entry.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_entry, target_entry)


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
        try:
            shutil.copytree(source, destination)
            _copy_includes(task_root, destination, self.task.data["workspace"].get("include", []))
        except Exception:
            if destination.exists():
                shutil.rmtree(destination)
            raise
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


class ValidatorWorkspace:
    """A disposable copy that receives private tests only for validation."""

    def __init__(
        self, config: BenchmarkConfig, task: TaskDefinition, model_workspace: Path, run_id: str
    ) -> None:
        self.config = config
        self.task = task
        self.model_workspace = model_workspace
        self.run_id = run_id
        self.path: Path | None = None

    def __enter__(self) -> Path:
        private_root = self.config.repository_path("private_tests")
        private_source = _ensure_inside(
            private_root, private_root / self.task.id, "private test source"
        )
        if not private_source.is_dir():
            raise WorkspaceError(
                f"Hidden validation is declared but private tests are missing: {private_source}"
            )
        _reject_symlinks(private_source)
        _reject_symlinks(self.model_workspace)

        work_root = self.config.repository_path("work")
        destination = _ensure_inside(
            work_root, work_root / f"{self.run_id}-validator", "validator workspace"
        )
        if destination.exists():
            raise WorkspaceError(f"Validator workspace already exists: {destination}")
        try:
            shutil.copytree(self.model_workspace, destination)
            _copy_overlay(private_source, destination)
        except Exception:
            if destination.exists():
                shutil.rmtree(destination)
            raise
        self.path = destination
        return destination

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self.path is None:
            return
        work_root = self.config.repository_path("work").resolve()
        target = self.path.resolve()
        try:
            target.relative_to(work_root)
        except ValueError as safety_error:
            raise WorkspaceError(
                f"Refusing to remove validator workspace outside {work_root}"
            ) from safety_error
        # Hidden material must never be retained, even when model workspaces are kept.
        shutil.rmtree(target)
