from __future__ import annotations

import difflib
from dataclasses import dataclass
from pathlib import Path

_GENERATED_DIRECTORIES = {
    ".gradle",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "out",
    "out-hidden",
    "target",
}


@dataclass(frozen=True)
class PatchMetrics:
    files_modified: list[str]
    expected_files_modified: list[str]
    unnecessary_files_modified: list[str]
    lines_added: int
    lines_removed: int
    relevant_file_precision: float | None
    relevant_file_recall: float | None

    def as_dict(self) -> dict[str, object]:
        return {
            "files_modified": self.files_modified,
            "expected_files_modified": self.expected_files_modified,
            "unnecessary_files_modified": self.unnecessary_files_modified,
            "lines_added": self.lines_added,
            "lines_removed": self.lines_removed,
            "relevant_file_precision": self.relevant_file_precision,
            "relevant_file_recall": self.relevant_file_recall,
        }


def snapshot_files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and not any(part in _GENERATED_DIRECTORIES for part in path.relative_to(root).parts)
    }


def _line_changes(before: bytes | None, after: bytes | None) -> tuple[int, int]:
    if before is None:
        try:
            return len(after.decode("utf-8").splitlines()), 0  # type: ignore[union-attr]
        except UnicodeDecodeError:
            return 0, 0
    if after is None:
        try:
            return 0, len(before.decode("utf-8").splitlines())
        except UnicodeDecodeError:
            return 0, 0
    try:
        old_lines = before.decode("utf-8").splitlines()
        new_lines = after.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return 0, 0
    added = removed = 0
    for operation, old_start, old_end, new_start, new_end in difflib.SequenceMatcher(
        None, old_lines, new_lines
    ).get_opcodes():
        if operation in {"insert", "replace"}:
            added += new_end - new_start
        if operation in {"delete", "replace"}:
            removed += old_end - old_start
    return added, removed


def calculate_patch_metrics(
    baseline: dict[str, bytes], workspace: Path, expected_files: list[str] | None
) -> PatchMetrics:
    before = baseline
    after = snapshot_files(workspace)
    modified = sorted(
        path for path in set(before) | set(after) if before.get(path) != after.get(path)
    )
    lines_added = lines_removed = 0
    for path in modified:
        added, removed = _line_changes(before.get(path), after.get(path))
        lines_added += added
        lines_removed += removed

    expected = sorted(set(expected_files or []))
    expected_set = set(expected)
    modified_set = set(modified)
    unnecessary = sorted(modified_set - expected_set) if expected_files is not None else []
    precision = None
    recall = None
    if expected_files is not None:
        precision = len(modified_set & expected_set) / len(modified_set) if modified_set else 0.0
        recall = len(modified_set & expected_set) / len(expected_set) if expected_set else 1.0
    return PatchMetrics(
        files_modified=modified,
        expected_files_modified=sorted(modified_set & expected_set),
        unnecessary_files_modified=unnecessary,
        lines_added=lines_added,
        lines_removed=lines_removed,
        relevant_file_precision=precision,
        relevant_file_recall=recall,
    )
