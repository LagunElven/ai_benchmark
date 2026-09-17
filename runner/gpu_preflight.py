"""Preparation and reproducibility checks for a remote GPU campaign."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from runner.catalogue import catalogue_coverage
from runner.config import load_benchmark_config, validate_document
from runner.discovery import TaskDefinition, discover_tasks
from runner.errors import ConfigurationError
from serving.benchmark import load_serving_config


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _git_command(root: Path, *arguments: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return completed.stdout.strip()


def _visible_task_files(task: TaskDefinition) -> list[Path]:
    """Return only files that can be copied into a model-visible workspace."""
    paths: set[Path] = {task.path, task.prompt_path}
    workspace = task.directory / task.data["workspace"]["source"]
    if workspace.is_dir():
        paths.update(
            path for path in workspace.rglob("*") if path.is_file() and not path.is_symlink()
        )
    for include in task.data["workspace"].get("include", []):
        source = task.directory / include["source"]
        if source.is_file() and not source.is_symlink():
            paths.add(source)
        elif source.is_dir():
            paths.update(
                path for path in source.rglob("*") if path.is_file() and not path.is_symlink()
            )
    return sorted(paths)


def visible_task_manifest(tasks: list[TaskDefinition], root: Path) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for task in tasks:
        files = []
        for path in _visible_task_files(task):
            files.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
        manifest.append(
            {
                "id": task.id,
                "revision": task.data["revision"],
                "files": files,
            }
        )
    return manifest


def _check(name: str, status: str, detail: Any = None) -> dict[str, Any]:
    result: dict[str, Any] = {"name": name, "status": status}
    if detail is not None:
        result["detail"] = detail
    return result


def load_gpu_plan(path: str | Path) -> dict[str, Any]:
    plan_path = Path(path).resolve()
    data_path = plan_path.parent.parent.parent / "schemas" / "gpu-campaign-plan.schema.json"
    from runner.config import load_structured_file

    data = load_structured_file(plan_path)
    validate_document(data, data_path, plan_path)
    ids = [campaign["id"] for campaign in data["campaigns"]]
    if len(ids) != len(set(ids)):
        raise ConfigurationError(f"Duplicate campaign ids in {plan_path}")
    variants = {variant["id"] for variant in data["model"]["artifact_variants"]}
    missing = sorted({campaign["artifact_variant"] for campaign in data["campaigns"]} - variants)
    if missing:
        raise ConfigurationError(f"Unknown artifact variants in {plan_path}: {', '.join(missing)}")
    variant_ids = [variant["id"] for variant in data["model"]["artifact_variants"]]
    if len(variant_ids) != len(set(variant_ids)):
        raise ConfigurationError(f"Duplicate artifact variant ids in {plan_path}")
    return data


def _selected_campaign(
    plan: dict[str, Any], campaign_id: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    campaign = next((item for item in plan["campaigns"] if item["id"] == campaign_id), None)
    if campaign is None:
        available = ", ".join(item["id"] for item in plan["campaigns"])
        raise ConfigurationError(f"Unknown campaign {campaign_id}; available: {available}")
    variant = next(
        item
        for item in plan["model"]["artifact_variants"]
        if item["id"] == campaign["artifact_variant"]
    )
    return campaign, variant


def _hash_document(path: Path) -> dict[str, Any]:
    return {"path": path.as_posix(), "sha256": sha256_file(path), "size_bytes": path.stat().st_size}


def build_preflight_manifest(
    *,
    config_path: str | Path,
    serving_config_path: str | Path,
    plan_path: str | Path,
    campaign_id: str,
    require_clean: bool = False,
) -> dict[str, Any]:
    config = load_benchmark_config(config_path)
    serving_config = load_serving_config(serving_config_path)
    plan = load_gpu_plan(plan_path)
    campaign, variant = _selected_campaign(plan, campaign_id)
    model_plan = plan["model"]
    planned_model_revision = variant.get("revision") or model_plan["revision"]
    root = config.root
    tasks = discover_tasks(config)
    coverage = catalogue_coverage(root)
    commit = _git_command(root, "rev-parse", "HEAD")
    status_output = _git_command(root, "status", "--porcelain", "--untracked-files=all")
    dirty_paths = status_output.splitlines() if status_output else []

    checks = [
        _check("benchmark_config", "passed"),
        _check("serving_config", "passed"),
        _check("git_commit", "passed" if commit else "failed", commit),
        _check(
            "git_clean",
            "passed" if not dirty_paths else ("failed" if require_clean else "warning"),
            dirty_paths,
        ),
        _check(
            "task_catalogue",
            "passed"
            if coverage["implemented_tasks"] == coverage["target_tasks"]
            and not any(
                coverage[key]
                for key in (
                    "missing_implemented",
                    "category_mismatches",
                    "missing_validation",
                    "unexpected_tasks",
                )
            )
            else "failed",
            coverage,
        ),
        _check(
            "hidden_tests",
            "passed" if all(task.has_hidden_validation for task in tasks) else "failed",
            {
                "tasks": len(tasks),
                "with_hidden_validation": sum(task.has_hidden_validation for task in tasks),
            },
        ),
        _check(
            "model_name",
            "passed" if config.data["model"]["name"] == plan["model"]["name"] else "failed",
            {"configured": config.data["model"]["name"], "planned": plan["model"]["name"]},
        ),
        _check(
            "quantization",
            "passed"
            if config.data["model"].get("quantization") == variant["quantization"]
            else "failed",
            {
                "configured": config.data["model"].get("quantization"),
                "planned": variant["quantization"],
            },
        ),
        _check(
            "dtype",
            "passed" if config.data["model"].get("dtype") == variant["dtype"] else "failed",
            {"configured": config.data["model"].get("dtype"), "planned": variant["dtype"]},
        ),
        _check(
            "model_source_repository",
            "passed"
            if config.data["model"].get("source_repository") == variant["source_repository"]
            else "failed",
            {
                "configured": config.data["model"].get("source_repository"),
                "planned": variant["source_repository"],
            },
        ),
        _check(
            "serving_model_name",
            "passed" if serving_config.data["model"] == plan["model"]["name"] else "failed",
            {"configured": serving_config.data["model"], "planned": plan["model"]["name"]},
        ),
        _check(
            "serving_quantization",
            "passed"
            if serving_config.data["model_metadata"].get("quantization") == variant["quantization"]
            else "failed",
            {
                "configured": serving_config.data["model_metadata"].get("quantization"),
                "planned": variant["quantization"],
            },
        ),
        _check(
            "serving_dtype",
            "passed"
            if serving_config.data["model_metadata"].get("dtype") == variant["dtype"]
            else "failed",
            {
                "configured": serving_config.data["model_metadata"].get("dtype"),
                "planned": variant["dtype"],
            },
        ),
        _check(
            "serving_model_source_repository",
            "passed"
            if serving_config.data["model_metadata"].get("source_repository")
            == variant["source_repository"]
            else "failed",
            {
                "configured": serving_config.data["model_metadata"].get("source_repository"),
                "planned": variant["source_repository"],
            },
        ),
        _check(
            "model_revision",
            "passed"
            if config.data["model"].get("revision") == planned_model_revision
            else "failed",
            {
                "configured": config.data["model"].get("revision"),
                "planned": planned_model_revision,
            },
        ),
        _check(
            "tokenizer_revision",
            "passed"
            if config.data["model"].get("tokenizer_revision") == model_plan["tokenizer_revision"]
            else "failed",
            {
                "configured": config.data["model"].get("tokenizer_revision"),
                "planned": model_plan["tokenizer_revision"],
            },
        ),
        _check(
            "serving_model_revision",
            "passed"
            if serving_config.data["model_metadata"].get("revision") == planned_model_revision
            else "failed",
            {
                "configured": serving_config.data["model_metadata"].get("revision"),
                "planned": planned_model_revision,
            },
        ),
        _check(
            "serving_tokenizer_revision",
            "passed"
            if serving_config.data["model_metadata"].get("tokenizer_revision")
            == model_plan["tokenizer_revision"]
            else "failed",
            {
                "configured": serving_config.data["model_metadata"].get("tokenizer_revision"),
                "planned": model_plan["tokenizer_revision"],
            },
        ),
        _check(
            "serving_engine",
            "passed"
            if plan["serving"]["engine"]
            and serving_config.data["serving"].get("engine") == plan["serving"]["engine"]
            else ("warning" if not plan["serving"]["engine"] else "failed"),
            {
                "configured": serving_config.data["serving"].get("engine"),
                "planned": plan["serving"]["engine"],
            },
        ),
        _check(
            "serving_engine_version",
            "passed"
            if plan["serving"]["engine_version"]
            and serving_config.data["serving"].get("engine_version")
            == plan["serving"]["engine_version"]
            else ("warning" if not plan["serving"]["engine_version"] else "failed"),
            {
                "configured": serving_config.data["serving"].get("engine_version"),
                "planned": plan["serving"]["engine_version"],
            },
        ),
    ]
    for field in (
        "kv_cache_dtype",
        "tensor_parallel_size",
        "pipeline_parallel_size",
        "max_model_length",
        "max_num_seqs",
        "reasoning_parser",
    ):
        planned = plan["serving"][field]
        configured_quality = config.data["serving"].get(field)
        configured_serving = serving_config.data["serving"].get(field)
        checks.append(
            _check(
                f"serving_{field}",
                "passed"
                if configured_quality == planned and configured_serving == planned
                else "failed",
                {
                    "quality_config": configured_quality,
                    "serving_config": configured_serving,
                    "planned": planned,
                },
            )
        )
    errors = [check["name"] for check in checks if check["status"] == "failed"]
    pending: list[str] = []
    if not model_plan["source_repository"]:
        pending.append("model.source_repository")
    if not model_plan["revision"]:
        pending.append("model.revision")
    if not model_plan["tokenizer_repository"]:
        pending.append("model.tokenizer_repository")
    if not model_plan["tokenizer_revision"]:
        pending.append("model.tokenizer_revision")
    if not variant["source_repository"]:
        pending.append(f"artifact_variants.{variant['id']}.source_repository")
    if not variant["revision"]:
        pending.append(f"artifact_variants.{variant['id']}.revision")
    if not variant["snapshot_url"]:
        pending.append(f"artifact_variants.{variant['id']}.snapshot_url")
    if not plan["serving"]["engine"]:
        pending.append("serving.engine")
    if not plan["serving"]["engine_version"]:
        pending.append("serving.engine_version")
    if (
        plan["serving"]["engine"]
        and serving_config.data["serving"].get("engine") != plan["serving"]["engine"]
    ):
        errors.append("serving_engine")
    if (
        plan["serving"]["engine_version"]
        and serving_config.data["serving"].get("engine_version")
        != plan["serving"]["engine_version"]
    ):
        errors.append("serving_engine_version")

    return {
        "schema_version": "1.0",
        "type": "gpu_campaign_preflight",
        "created_at": _utc_now(),
        "campaign": {
            **campaign,
            "planned_model": model_plan["name"],
            "planned_model_source_repository": variant["source_repository"],
            "planned_model_revision": planned_model_revision,
            "planned_tokenizer_repository": model_plan["tokenizer_repository"],
            "planned_tokenizer_revision": model_plan["tokenizer_revision"],
            "planned_quantization": variant["quantization"],
            "planned_dtype": variant["dtype"],
        },
        "plan": {
            "path": str(Path(plan_path).resolve().relative_to(root).as_posix()),
            "version": plan["version"],
            "sha256": sha256_file(Path(plan_path).resolve()),
        },
        "repository": {
            "root": str(root),
            "git_commit": commit,
            "dirty_paths": dirty_paths,
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "inputs": {
            "benchmark_config": _hash_document(Path(config_path).resolve()),
            "serving_config": _hash_document(Path(serving_config_path).resolve()),
            "visible_tasks": visible_task_manifest(tasks, root),
            "visible_task_count": len(tasks),
        },
        "checks": checks,
        "errors": errors,
        "pending_decisions": pending,
        "status": "failed" if errors else ("pending" if pending else "ready"),
        "next_step": (
            "Fill the pending plan values, commit the repository, then rerun this preflight."
            if pending or errors
            else "Rent the target GPU and run the remote host preflight before starting the server."
        ),
        "serving_config_summary": {
            "model": serving_config.data["model"],
            "endpoint": serving_config.data["endpoint"]["base_url"],
            "matrix_cases": (
                len(serving_config.data["matrix"]["concurrency"])
                * len(serving_config.data["matrix"]["context_tokens"])
                * len(serving_config.data["matrix"]["prefix_modes"])
            ),
        },
    }


def write_preflight_manifest(manifest: dict[str, Any], output_path: str | Path) -> Path:
    path = Path(output_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path
