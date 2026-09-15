"""Legacy fixture metadata and optional native toolchain detection."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

_TOOLCHAIN_CANDIDATES = {
    "gnu_cobol": ("cobc",),
    "delphi": ("dcc32", "dcc64"),
    "windev": ("wdcompiler", "wdcomp"),
}


def load_legacy_fixture(path: str | Path, schema_path: str | Path | None = None) -> dict[str, Any]:
    fixture_path = Path(path)
    try:
        value = json.loads(fixture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read legacy fixture {fixture_path}: {exc}") from exc
    selected_schema = (
        Path(schema_path)
        if schema_path is not None
        else Path(__file__).resolve().parents[1] / "schemas" / "legacy-fixture.schema.json"
    )
    try:
        schema = json.loads(selected_schema.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read legacy fixture schema {selected_schema}: {exc}") from exc
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value),
        key=lambda error: list(error.path),
    )
    if errors:
        location = ".".join(str(part) for part in errors[0].absolute_path) or "<root>"
        raise ValueError(f"Legacy fixture schema error at {location}: {errors[0].message}")
    return value


def detect_toolchains() -> dict[str, dict[str, Any]]:
    detected: dict[str, dict[str, Any]] = {}
    for name, candidates in _TOOLCHAIN_CANDIDATES.items():
        executable = next((shutil.which(candidate) for candidate in candidates), None)
        version = None
        if executable:
            try:
                completed = subprocess.run(
                    [executable, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                version = (completed.stdout or completed.stderr).splitlines()[0][:200] or None
            except (OSError, subprocess.SubprocessError):
                version = None
        detected[name] = {
            "available": executable is not None,
            "path": executable,
            "version": version,
            "candidates": list(candidates),
        }
    detected["abal"] = {
        "available": False,
        "path": None,
        "version": None,
        "candidates": [],
        "note": (
            "No portable ABAL compiler is assumed; use supplied documentation "
            "or Java equivalence."
        ),
    }
    return detected


def compare_vector_outputs(expected: list[Any], actual: list[Any]) -> dict[str, Any]:
    """Compare ordered legacy/target outputs without an LLM judge."""
    mismatches = [
        {
            "index": index,
            "expected": expected_value,
            "actual": actual[index] if index < len(actual) else None,
        }
        for index, expected_value in enumerate(expected)
        if index >= len(actual) or actual[index] != expected_value
    ]
    if len(actual) > len(expected):
        mismatches.extend(
            {"index": index, "expected": None, "actual": value}
            for index, value in enumerate(actual[len(expected):], start=len(expected))
        )
    return {
        "passed": not mismatches,
        "expected_count": len(expected),
        "actual_count": len(actual),
        "mismatches": mismatches,
    }
