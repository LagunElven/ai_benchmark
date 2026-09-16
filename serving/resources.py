"""Best-effort host/GPU resource sampling with explicit unavailable values."""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Any


def _number(value: str) -> int | float | None:
    text = value.strip()
    if not text or text.lower() in {"n/a", "not supported", "unknown"}:
        return None
    try:
        return float(text) if "." in text else int(text)
    except ValueError:
        return None


def sample_resources() -> dict[str, Any]:
    result: dict[str, Any] = {
        "gpu": {"available": False, "devices": [], "error": None},
        "host": {"cpu_percent": None, "memory_used_bytes": None, "memory_total_bytes": None},
    }
    executable = shutil.which("nvidia-smi")
    if executable:
        try:
            completed = subprocess.run(
                [
                    executable,
                    "--query-gpu=index,name,memory.used,memory.total,utilization.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            devices = []
            for line in completed.stdout.splitlines():
                fields = [field.strip() for field in line.split(",")]
                if len(fields) != 5:
                    continue
                devices.append(
                    {
                        "index": _number(fields[0]),
                        "name": fields[1],
                        "memory_used_mb": _number(fields[2]),
                        "memory_total_mb": _number(fields[3]),
                        "utilization_percent": _number(fields[4]),
                    }
                )
            result["gpu"] = {
                "available": bool(devices),
                "devices": devices,
                "error": None if devices else (completed.stderr.strip() or None),
            }
        except (OSError, subprocess.SubprocessError) as exc:
            result["gpu"]["error"] = str(exc)
    try:
        import psutil

        memory = psutil.virtual_memory()
        result["host"] = {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "memory_used_bytes": memory.used,
            "memory_total_bytes": memory.total,
        }
    except ImportError:
        result["host"]["error"] = "psutil unavailable"
    return result


def resource_summary(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Keep both point samples; never imply a peak when no sampler was available."""
    return {"before": before, "after": after}


def json_safe(value: Any) -> Any:
    """Normalize a resource object before serializing it in a raw result."""
    return json.loads(json.dumps(value, allow_nan=False))
