from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from runner.errors import ValidationError

_GENERATED_CACHE_DIRECTORIES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


def _clean_generated_caches(workspace: Path) -> None:
    for path in sorted(workspace.rglob("*"), reverse=True):
        if path.name not in _GENERATED_CACHE_DIRECTORIES:
            continue
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)


@dataclass(frozen=True)
class CommandResult:
    name: str
    command: list[str]
    cwd: str
    exit_code: int | None
    timed_out: bool
    duration_seconds: float
    stdout: str
    stderr: str

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    def summary(self, log_path: str) -> dict[str, Any]:
        return {
            "name": self.name,
            "command": self.command,
            "cwd": self.cwd,
            "exit_code": self.exit_code,
            "timed_out": self.timed_out,
            "duration_seconds": self.duration_seconds,
            "passed": self.passed,
            "log": log_path,
        }


def _command_arguments(command: str | list[str]) -> list[str]:
    if isinstance(command, list):
        arguments = command
    else:
        arguments = shlex.split(command, posix=os.name != "nt")
    if not arguments or any(not isinstance(value, str) or not value for value in arguments):
        raise ValidationError("Validator command must contain non-empty string arguments")
    return arguments


def _safe_cwd(workspace: Path, relative: str) -> Path:
    candidate = (workspace / relative).resolve()
    try:
        candidate.relative_to(workspace.resolve())
    except ValueError as exc:
        raise ValidationError(f"Validator cwd escapes workspace: {relative}") from exc
    if not candidate.is_dir():
        raise ValidationError(f"Validator cwd is not a directory: {relative}")
    return candidate


def _validator_environment() -> dict[str, str]:
    allowed = {
        "COMSPEC",
        "JAVA_HOME",
        "LANG",
        "LC_ALL",
        "M2_HOME",
        "NUMBER_OF_PROCESSORS",
        "OS",
        "PATH",
        "PATHEXT",
        "SYSTEMDRIVE",
        "SYSTEMROOT",
        "TEMP",
        "TMP",
        "WINDIR",
    }
    return {key: value for key, value in os.environ.items() if key.upper() in allowed}


def run_validator(
    specification: dict[str, Any], workspace: Path, default_timeout: int
) -> CommandResult:
    _clean_generated_caches(workspace)
    arguments = _command_arguments(specification["command"])
    cwd_relative = specification.get("cwd", ".")
    cwd = _safe_cwd(workspace, cwd_relative)
    reported_cwd = Path(cwd_relative).as_posix()
    timeout = specification.get("timeout_seconds", default_timeout)
    name = specification.get("name", " ".join(arguments))
    started = time.monotonic()
    try:
        completed = subprocess.run(
            arguments,
            cwd=cwd,
            env=_validator_environment(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            shell=False,
            check=False,
        )
        return CommandResult(
            name=name,
            command=arguments,
            cwd=reported_cwd,
            exit_code=completed.returncode,
            timed_out=False,
            duration_seconds=time.monotonic() - started,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = (
            exc.stdout.decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else exc.stdout
        )
        stderr = (
            exc.stderr.decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else exc.stderr
        )
        return CommandResult(
            name=name,
            command=arguments,
            cwd=reported_cwd,
            exit_code=None,
            timed_out=True,
            duration_seconds=time.monotonic() - started,
            stdout=stdout or "",
            stderr=stderr or "",
        )
    except OSError as exc:
        raise ValidationError(f"Could not start validator {name!r}: {exc}") from exc


def format_log(result: CommandResult) -> str:
    command = " ".join(result.command)
    return (
        f"name: {result.name}\n"
        f"command: {command}\n"
        f"cwd: {result.cwd}\n"
        f"exit_code: {result.exit_code}\n"
        f"timed_out: {str(result.timed_out).lower()}\n"
        f"duration_seconds: {result.duration_seconds:.6f}\n"
        "\n[stdout]\n"
        f"{result.stdout}"
        "\n[stderr]\n"
        f"{result.stderr}"
    )
