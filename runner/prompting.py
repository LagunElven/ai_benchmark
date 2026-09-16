from __future__ import annotations

from pathlib import Path

from runner.discovery import TaskDefinition
from runner.errors import WorkspaceError

SYSTEM_PROMPT = """You are completing a software benchmark task in an isolated workspace.
Return only a JSON object matching file_changes_v1:
{"changes":[{"path":"relative/path","content":"complete UTF-8 file content"}]}
Use forward-slash relative paths. Do not include markdown fences, explanations, commands,
absolute paths, parent traversal, or files that do not need to change. The content value is
a JSON string: escape every newline as \\n, every backslash as \\\\, and every embedded
double quote as \\". Never place a literal line break inside a JSON string."""


def _is_probably_binary(content: bytes) -> bool:
    return b"\x00" in content[:4096]


def build_messages(
    task: TaskDefinition, workspace: Path, max_context_bytes: int
) -> list[dict[str, str]]:
    prompt = task.prompt_path.read_text(encoding="utf-8")
    sections = [f"# Task\n\n{prompt.rstrip()}", "# Workspace files"]
    consumed = len(prompt.encode("utf-8"))

    for path in sorted(item for item in workspace.rglob("*") if item.is_file()):
        if path.is_symlink():
            raise WorkspaceError(f"Workspace contains a symlink: {path}")
        relative = path.relative_to(workspace).as_posix()
        content = path.read_bytes()
        if _is_probably_binary(content):
            sections.append(f"## {relative}\n\n[binary file omitted]")
            consumed += len(relative.encode("utf-8")) + 32
            continue
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise WorkspaceError(f"Text workspace file is not valid UTF-8: {relative}") from exc
        addition = f"## {relative}\n\n```text\n{text}\n```"
        consumed += len(addition.encode("utf-8"))
        if consumed > max_context_bytes:
            raise WorkspaceError(
                f"Task {task.id} exceeds runner.max_context_bytes ({max_context_bytes})"
            )
        sections.append(addition)

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "\n\n".join(sections)},
    ]
