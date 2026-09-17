from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any

from runner.errors import ChangeProtocolError


def _parse_payload(content: str) -> dict[str, Any]:
    stripped = content.strip()
    if stripped.startswith("```"):
        stripped = stripped[3:]
        if stripped.lower().startswith("json"):
            stripped = stripped[4:]
        stripped = stripped.lstrip()
        if stripped.endswith("```"):
            stripped = stripped[:-3].rstrip()
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ChangeProtocolError(f"Model response is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict) or set(payload) != {"changes"}:
        raise ChangeProtocolError("Response must contain only a 'changes' array")
    if not isinstance(payload["changes"], list):
        raise ChangeProtocolError("'changes' must be an array")
    return payload


def _safe_destination(workspace: Path, relative: str) -> Path:
    if not relative or "\\" in relative:
        raise ChangeProtocolError(f"Invalid POSIX relative path: {relative!r}")
    path = PurePosixPath(relative)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ChangeProtocolError(f"Unsafe change path: {relative!r}")
    destination = workspace.joinpath(*path.parts).resolve()
    try:
        destination.relative_to(workspace.resolve())
    except ValueError as exc:
        raise ChangeProtocolError(f"Change path escapes workspace: {relative!r}") from exc
    return destination


def apply_file_changes(content: str, workspace: Path) -> list[str]:
    payload = _parse_payload(content)
    if len(payload["changes"]) > 100:
        raise ChangeProtocolError("A response may modify at most 100 files")
    changed: list[str] = []
    seen: set[str] = set()
    for index, change in enumerate(payload["changes"]):
        if not isinstance(change, dict) or set(change) != {"path", "content"}:
            raise ChangeProtocolError(
                f"changes[{index}] must contain only string 'path' and 'content' fields"
            )
        relative = change["path"]
        file_content = change["content"]
        if not isinstance(relative, str) or not isinstance(file_content, str):
            raise ChangeProtocolError(f"changes[{index}] path and content must be strings")
        destination = _safe_destination(workspace, relative)
        normalized = PurePosixPath(relative).as_posix()
        if normalized in seen:
            raise ChangeProtocolError(f"Duplicate change path: {normalized}")
        seen.add(normalized)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and destination.is_symlink():
            raise ChangeProtocolError(f"Refusing to replace symlink: {normalized}")
        destination.write_text(file_content, encoding="utf-8", newline="")
        changed.append(normalized)
    return changed
