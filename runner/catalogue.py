"""Quality-task catalogue loading and coverage checks."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from runner.config import load_benchmark_config, load_structured_file, validate_document
from runner.discovery import discover_tasks
from runner.errors import ConfigurationError


def load_catalogue(path: str | Path) -> dict[str, Any]:
    catalogue_path = Path(path).resolve()
    data = load_structured_file(catalogue_path)
    schema_path = catalogue_path.parent / "schemas" / "catalogue.schema.json"
    validate_document(data, schema_path, catalogue_path)
    categories = data["categories"]
    category_ids = [category["id"] for category in categories]
    if len(category_ids) != len(set(category_ids)):
        raise ConfigurationError(f"Duplicate catalogue categories in {catalogue_path}")
    task_ids = [task["id"] for category in categories for task in category["tasks"]]
    if len(task_ids) != len(set(task_ids)):
        raise ConfigurationError(f"Duplicate catalogue task ids in {catalogue_path}")
    for category in categories:
        if category["target"] != len(category["tasks"]):
            raise ConfigurationError(
                f"Catalogue target for {category['id']} does not match its task list"
            )
    return data


def catalogue_coverage(
    repository_root: str | Path,
    catalogue_path: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repository_root).resolve()
    path = Path(catalogue_path) if catalogue_path else root / "catalogue.yaml"
    if not path.is_absolute():
        path = root / path
    catalogue = load_catalogue(path)
    config = load_benchmark_config(root / "benchmark.yaml")
    discovered = discover_tasks(config)
    discovered_by_id = {task.id: task for task in discovered}
    entries = {
        task["id"]: (category["id"], task)
        for category in catalogue["categories"]
        for task in category["tasks"]
    }
    implemented = [
        task_id for task_id, (_, task) in entries.items() if task["status"] == "implemented"
    ]
    missing_implemented = sorted(
        task_id for task_id in implemented if task_id not in discovered_by_id
    )
    category_mismatches = sorted(
        {
            task_id
            for task_id, (category_id, _) in entries.items()
            if task_id in discovered_by_id
            and discovered_by_id[task_id].data["category"] != category_id
        }
    )
    missing_validation = sorted(
        task_id
        for task_id in implemented
        if task_id in discovered_by_id
        and (
            not discovered_by_id[task_id].data["validation"]["public"]
            or not discovered_by_id[task_id].has_hidden_validation
            or not (config.repository_path("private_tests") / task_id).is_dir()
        )
    )
    unexpected = sorted(task_id for task_id in discovered_by_id if task_id not in entries)
    status_counts = Counter(task["status"] for _, task in entries.values())
    category_summary: dict[str, dict[str, int]] = {}
    for category in catalogue["categories"]:
        counts = Counter(task["status"] for task in category["tasks"])
        category_summary[category["id"]] = {
            "target": category["target"],
            "implemented": counts.get("implemented", 0),
            "planned": counts.get("planned", 0),
            "generated": counts.get("generated", 0),
        }
    return {
        "catalogue": str(path),
        "target_tasks": len(entries),
        "discovered_tasks": len(discovered_by_id),
        "implemented_tasks": status_counts.get("implemented", 0),
        "planned_tasks": status_counts.get("planned", 0),
        "generated_tasks": status_counts.get("generated", 0),
        "missing_implemented": missing_implemented,
        "category_mismatches": category_mismatches,
        "missing_validation": missing_validation,
        "unexpected_tasks": unexpected,
        "categories": category_summary,
    }
