"""Best-effort host/GPU resource sampling with explicit unavailable values."""

from __future__ import annotations

import json
import shutil
import subprocess
import threading
import time
from datetime import UTC, datetime
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


class ResourceMonitor:
    """Sample the runner host while a serving case is in flight."""

    def __init__(self, interval_seconds: float = 1.0) -> None:
        self.interval_seconds = interval_seconds
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._started = 0.0
        self._samples: list[dict[str, Any]] = []

    def _sample(self) -> None:
        self._samples.append(
            {
                "captured_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "offset_seconds": max(0.0, time.monotonic() - self._started),
                "metrics": sample_resources(),
            }
        )

    def _run(self) -> None:
        while not self._stop.wait(self.interval_seconds):
            self._sample()

    def start(self) -> None:
        self._started = time.monotonic()
        self._sample()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> dict[str, Any]:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=self.interval_seconds + 5.0)
        self._sample()
        return resource_summary(self._samples, self.interval_seconds)


def resource_summary(samples: list[dict[str, Any]], interval_seconds: float) -> dict[str, Any]:
    """Preserve samples and report sampled maxima, scoped to the runner host."""
    metrics = [item.get("metrics", {}) for item in samples]
    gpu_memory: dict[str, float] = {}
    gpu_utilization: dict[str, float] = {}
    host_cpu: list[float] = []
    host_memory: list[int] = []
    for sample in metrics:
        gpu = sample.get("gpu", {})
        for device in gpu.get("devices", []):
            index = str(device.get("index", "unknown"))
            memory_used = device.get("memory_used_mb")
            utilization = device.get("utilization_percent")
            if isinstance(memory_used, (int, float)):
                gpu_memory[index] = max(gpu_memory.get(index, memory_used), memory_used)
            if isinstance(utilization, (int, float)):
                gpu_utilization[index] = max(gpu_utilization.get(index, utilization), utilization)
        host = sample.get("host", {})
        cpu = host.get("cpu_percent")
        memory = host.get("memory_used_bytes")
        if isinstance(cpu, (int, float)):
            host_cpu.append(cpu)
        if isinstance(memory, int):
            host_memory.append(memory)
    return {
        "source_host_role": "benchmark_runner",
        "sample_interval_seconds": interval_seconds,
        "sample_count": len(samples),
        "samples": samples,
        "sampled_peaks": {
            "gpu_memory_used_mb_by_device": gpu_memory,
            "gpu_utilization_percent_by_device": gpu_utilization,
            "host_cpu_percent": max(host_cpu) if host_cpu else None,
            "host_memory_used_bytes": max(host_memory) if host_memory else None,
        },
        "before": metrics[0] if metrics else None,
        "after": metrics[-1] if metrics else None,
    }


def json_safe(value: Any) -> Any:
    """Normalize a resource object before serializing it in a raw result."""
    return json.loads(json.dumps(value, allow_nan=False))
