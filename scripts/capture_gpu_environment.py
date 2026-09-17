"""Capture the remote host fingerprint before a GPU campaign starts.

This script is intentionally independent from the benchmark task runner. Copy it
to a rented host or run it from a checkout inside the host container. It records
diagnostics, not credentials or model contents.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from serving.resources import sample_resources  # noqa: E402


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _command(command: list[str], timeout: int = 15) -> dict[str, Any]:
    executable = shutil.which(command[0])
    if executable is None:
        return {
            "available": False,
            "command": command,
            "stdout": "",
            "stderr": "not found",
            "returncode": None,
        }
    try:
        completed = subprocess.run(
            [executable, *command[1:]],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "available": True,
            "command": command,
            "stdout": "",
            "stderr": str(exc),
            "returncode": None,
        }
    return {
        "available": True,
        "command": command,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "returncode": completed.returncode,
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def capture_environment(
    output_path: str | Path | None = None,
    *,
    model_repository: str | None = None,
    model_revision: str | None = None,
    tokenizer_repository: str | None = None,
    tokenizer_revision: str | None = None,
    model_file: str | Path | None = None,
    expected_sha256: str | None = None,
) -> dict[str, Any]:
    commands = {
        "nvidia_smi": _command(["nvidia-smi"]),
        "nvidia_smi_query": _command(
            [
                "nvidia-smi",
                "--query-gpu=index,name,uuid,memory.total,driver_version,temperature.gpu",
                "--format=csv,noheader,nounits",
            ]
        ),
        "nvcc": _command(["nvcc", "--version"]),
        "docker": _command(["docker", "version", "--format", "{{.Server.Version}}"]),
        "vllm": _command(["vllm", "--version"]),
        "git": _command(["git", "--version"]),
        "python": _command([sys.executable, "--version"]),
    }
    disk = shutil.disk_usage(Path.cwd())
    result = {
        "schema_version": "1.0",
        "type": "remote_gpu_host_preflight",
        "captured_at": _utc_now(),
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python": platform.python_version(),
            "cwd": str(Path.cwd()),
            "disk": {
                "path": str(Path.cwd()),
                "total_bytes": disk.total,
                "free_bytes": disk.free,
            },
        },
        "commands": commands,
        "resources": sample_resources(),
    }
    if any(
        value is not None
        for value in (
            model_repository,
            model_revision,
            tokenizer_repository,
            tokenizer_revision,
        )
    ):
        result["model"] = {
            "repository": model_repository,
            "revision": model_revision,
            "tokenizer_repository": tokenizer_repository,
            "tokenizer_revision": tokenizer_revision,
        }
    if model_file is not None:
        path = Path(model_file).resolve()
        artifact: dict[str, Any] = {"path": str(path), "exists": path.is_file()}
        if path.is_file():
            artifact["size_bytes"] = path.stat().st_size
            artifact["sha256"] = _sha256_file(path)
            if expected_sha256:
                artifact["sha256_matches"] = artifact["sha256"].lower() == expected_sha256.lower()
        elif expected_sha256:
            artifact["sha256_matches"] = False
        result["model_artifact"] = artifact
    if output_path is not None:
        path = Path(output_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return result


def _device_matches(
    result: dict[str, Any],
    expected_gpu: str | None,
    min_memory_gb: float | None,
    expected_gpu_count: int | None,
) -> tuple[bool, str]:
    devices = result["resources"]["gpu"]["devices"]
    if not devices:
        return False, "nvidia-smi did not report a GPU"
    if expected_gpu_count is not None and len(devices) != expected_gpu_count:
        return False, f"expected {expected_gpu_count} GPU(s) but found {len(devices)}"
    if expected_gpu and not all(
        expected_gpu.lower() in str(device["name"]).lower() for device in devices
    ):
        names = ", ".join(str(device["name"]) for device in devices)
        return False, f"expected '{expected_gpu}' but found {names}"
    if min_memory_gb is not None:
        required_mb = min_memory_gb * 1024
        too_small = [device for device in devices if (device["memory_total_mb"] or 0) < required_mb]
        if too_small:
            return False, f"at least one GPU has less than {min_memory_gb:g} GiB"
    return True, f"{len(devices)} GPU(s) detected"


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("remote-gpu-preflight.json"))
    parser.add_argument("--expected-gpu")
    parser.add_argument("--expected-gpu-count", type=int)
    parser.add_argument("--min-memory-gb", type=float)
    parser.add_argument("--model-repository")
    parser.add_argument("--model-revision")
    parser.add_argument("--tokenizer-repository")
    parser.add_argument("--tokenizer-revision")
    parser.add_argument("--model-file", type=Path)
    parser.add_argument("--expected-sha256")
    options = parser.parse_args(arguments)
    result = capture_environment(
        options.output,
        model_repository=options.model_repository,
        model_revision=options.model_revision,
        tokenizer_repository=options.tokenizer_repository,
        tokenizer_revision=options.tokenizer_revision,
        model_file=options.model_file,
        expected_sha256=options.expected_sha256,
    )
    passed, detail = _device_matches(
        result,
        options.expected_gpu,
        options.min_memory_gb,
        options.expected_gpu_count,
    )
    result["checks"] = [
        {"name": "gpu", "status": "passed" if passed else "failed", "detail": detail}
    ]
    artifact = result.get("model_artifact")
    if isinstance(artifact, dict) and (
        not artifact["exists"] or artifact.get("sha256_matches") is False
    ):
        result["checks"].append(
            {
                "name": "model_artifact",
                "status": "failed",
                "detail": "model file is missing or SHA-256 does not match",
            }
        )
        passed = False
        detail = f"{detail}; model artifact check failed"
    result["status"] = "ready" if passed else "failed"
    options.output.resolve().write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": result["status"],
                "output": str(options.output.resolve()),
                "detail": detail,
            },
            ensure_ascii=False,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
