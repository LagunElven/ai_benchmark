"""Post-run deterministic metric extractors that keep answer keys private."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runner.config import BenchmarkConfig
from runner.discovery import TaskDefinition
from runner.document_metrics import score_fields


def _safe_file(base: Path, relative: str) -> Path:
    candidate_path = Path(relative)
    if candidate_path.is_absolute() or ".." in candidate_path.parts:
        raise ValueError("metric path must stay within its configured directory")
    base_path = base.resolve()
    candidate = base_path / candidate_path
    current = base_path
    for part in candidate_path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("metric input may not be a symlink")
    resolved = candidate.resolve()
    try:
        resolved.relative_to(base_path)
    except ValueError as exc:
        raise ValueError("metric path resolves outside its configured directory") from exc
    return resolved


def extract_task_metrics(
    config: BenchmarkConfig, task: TaskDefinition, model_workspace: Path
) -> dict[str, Any]:
    """Score configured structured-document outputs after all model feedback ends."""
    extracted: dict[str, Any] = {}
    private_task_root = config.repository_path("private_tests") / task.id
    for specification in task.data.get("metric_extractors", []):
        if specification.get("type") != "document_fields":
            continue
        name = specification["name"]
        try:
            expected_path = _safe_file(private_task_root, specification["expected"])
            actual_path = _safe_file(model_workspace, specification["actual"])
            expected_value = json.loads(expected_path.read_text(encoding="utf-8"))
            if not isinstance(expected_value, dict):
                raise ValueError("document ground truth must be a JSON object")
            try:
                actual_value = json.loads(actual_path.read_text(encoding="utf-8"))
            except FileNotFoundError:
                actual_value = None
            actual = actual_value if isinstance(actual_value, dict) else None
            schema = None
            if specification.get("schema"):
                schema_path = _safe_file(private_task_root, specification["schema"])
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
            extracted[name] = {
                "status": "scored",
                **score_fields(expected_value, actual, schema=schema),
            }
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            extracted[name] = {"status": "unavailable", "error_type": type(exc).__name__}
    return extracted
