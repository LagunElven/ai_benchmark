from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from runner.errors import ConfigurationError


def _format_error(error: Any) -> str:
    location = ".".join(str(part) for part in error.absolute_path) or "<root>"
    return f"{location}: {error.message}"


def load_structured_file(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as stream:
            value = yaml.safe_load(stream)
    except OSError as exc:
        raise ConfigurationError(f"Cannot read {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ConfigurationError(f"{path} must contain a mapping at its root")
    return value


def validate_document(document: dict[str, Any], schema_path: Path, source: Path) -> None:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"Cannot load schema {schema_path}: {exc}") from exc
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(document), key=lambda item: list(item.absolute_path))
    if errors:
        details = "; ".join(_format_error(error) for error in errors)
        raise ConfigurationError(f"Schema validation failed for {source}: {details}")


def resolve_inside(root: Path, relative: str, label: str) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ConfigurationError(f"{label} resolves outside the repository: {relative}") from exc
    return candidate


@dataclass(frozen=True)
class BenchmarkConfig:
    root: Path
    path: Path
    data: dict[str, Any]

    def repository_path(self, key: str) -> Path:
        return resolve_inside(self.root, self.data["paths"][key], f"paths.{key}")

    @property
    def schema_dir(self) -> Path:
        return self.root / "schemas"


def load_benchmark_config(path: str | Path) -> BenchmarkConfig:
    config_path = Path(path).resolve()
    root = config_path.parent
    data = load_structured_file(config_path)
    validate_document(data, root / "schemas" / "benchmark-config.schema.json", config_path)
    config = BenchmarkConfig(root=root, path=config_path, data=data)
    for key in ("tasks", "private_tests", "results", "work"):
        config.repository_path(key)
    return config
