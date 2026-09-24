"""Collect remote NVIDIA GPU telemetry through an independent SSH session."""

from __future__ import annotations

import csv
import ipaddress
import json
import re
import shutil
import subprocess
import threading
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

QUERY_FIELDS = (
    "timestamp,index,name,uuid,driver_version,memory.used,memory.total,"
    "utilization.gpu,temperature.gpu,power.draw,power.limit"
)
USER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
HOSTNAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def add_remote_gpu_arguments(parser: Any) -> None:
    """Add the shared optional remote GPU sampling arguments to a CLI parser."""
    parser.add_argument("--remote-gpu-ssh-host", help="remote GPU host name or IP address")
    parser.add_argument("--remote-gpu-ssh-user", help="SSH user on the remote GPU host")
    parser.add_argument("--remote-gpu-ssh-port", type=int, default=22)
    parser.add_argument("--remote-gpu-ssh-key", type=Path, help="private key file for OpenSSH")
    parser.add_argument("--remote-gpu-sample-interval-seconds", type=int, default=1)


def remote_gpu_monitor_from_options(parser: Any, options: Any) -> RemoteGpuMonitor:
    """Build a monitor from shared CLI options, reporting invalid input via argparse."""
    host = options.remote_gpu_ssh_host
    user = options.remote_gpu_ssh_user
    key_file = options.remote_gpu_ssh_key
    requested = (
        bool(host)
        or bool(user)
        or key_file is not None
        or options.remote_gpu_ssh_port != 22
        or options.remote_gpu_sample_interval_seconds != 1
    )
    if not requested:
        return RemoteGpuMonitor()
    if not host or not user:
        parser.error("--remote-gpu-ssh-host and --remote-gpu-ssh-user must be supplied together")
    try:
        return RemoteGpuMonitor(
            host=host,
            user=user,
            port=options.remote_gpu_ssh_port,
            key_file=key_file,
            interval_seconds=options.remote_gpu_sample_interval_seconds,
        )
    except ValueError as exc:
        parser.error(str(exc))
    raise AssertionError("argparse.error must exit")


def _number(value: str) -> int | float | None:
    normalized = value.strip()
    if not normalized or normalized.lower() in {"n/a", "not supported", "unknown"}:
        return None
    try:
        number = float(normalized) if "." in normalized else int(normalized)
    except ValueError:
        return None
    if isinstance(number, float) and not number.is_integer():
        return number
    return int(number)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


class RemoteGpuMonitor:
    """Stream nvidia-smi samples over SSH into a per-campaign JSONL sidecar."""

    def __init__(
        self,
        *,
        host: str | None = None,
        user: str | None = None,
        port: int = 22,
        key_file: Path | None = None,
        interval_seconds: int = 1,
    ) -> None:
        self.enabled = host is not None or user is not None or key_file is not None
        self.host = host
        self.user = user
        self.port = port
        self.key_file = key_file.expanduser().resolve() if key_file else None
        self.interval_seconds = interval_seconds
        self._process: subprocess.Popen[str] | None = None
        self._reader: threading.Thread | None = None
        self._stderr_reader: threading.Thread | None = None
        self._lock = threading.Lock()
        self._stop_requested = False
        self._capture_started_at: str | None = None
        self._capture_ended_at: str | None = None
        self._capture_started_monotonic: float | None = None
        self._samples_path: Path | None = None
        self._error_lines: list[str] = []
        self._sample_count = 0
        self._devices: dict[str, dict[str, Any]] = {}
        self._error: str | None = None
        self._unexpected_exit = False
        self._target = self._validate_target()

    def _validate_target(self) -> str | None:
        if not self.enabled:
            return None
        if not self.host or not self.user:
            raise ValueError("remote GPU SSH sampling requires both a host and a user")
        if not USER_PATTERN.fullmatch(self.user):
            raise ValueError("--remote-gpu-ssh-user contains unsupported characters")
        if not 1 <= self.port <= 65535:
            raise ValueError("--remote-gpu-ssh-port must be between 1 and 65535")
        if not 1 <= self.interval_seconds <= 60:
            raise ValueError("--remote-gpu-sample-interval-seconds must be between 1 and 60")
        try:
            address = ipaddress.ip_address(self.host)
            destination_host = f"[{address.compressed}]" if address.version == 6 else address.compressed
        except ValueError:
            if not HOSTNAME_PATTERN.fullmatch(self.host):
                raise ValueError("--remote-gpu-ssh-host must be a host name or IP address")
            destination_host = self.host
        if self.key_file is not None and not self.key_file.is_file():
            raise ValueError(f"SSH private key file does not exist: {self.key_file}")
        return f"{self.user}@{destination_host}"

    def start(self, samples_path: Path) -> None:
        """Start sampling; connection failures are recorded and do not stop a benchmark."""
        if not self.enabled:
            return
        self._capture_started_at = _utc_now()
        self._capture_started_monotonic = time.monotonic()
        ssh = shutil.which("ssh")
        if ssh is None:
            self._error = "OpenSSH client executable not found on the benchmark runner"
            return
        self._samples_path = samples_path
        command = [
            ssh,
            "-T",
            "-p",
            str(self.port),
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=10",
            "-o",
            "ServerAliveInterval=5",
            "-o",
            "ServerAliveCountMax=2",
        ]
        if self.key_file is not None:
            command.extend(["-i", str(self.key_file)])
        command.extend(
            [
                self._target or "",
                "nvidia-smi --query-gpu="
                + QUERY_FIELDS
                + " --format=csv,noheader,nounits --loop="
                + str(self.interval_seconds),
            ]
        )
        try:
            self._process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except OSError as exc:
            self._error = f"Unable to start OpenSSH: {exc}"
            return
        self._reader = threading.Thread(target=self._read_samples, daemon=True)
        self._stderr_reader = threading.Thread(target=self._read_errors, daemon=True)
        self._reader.start()
        self._stderr_reader.start()

    def _read_errors(self) -> None:
        process = self._process
        if process is None or process.stderr is None:
            return
        for line in process.stderr:
            with self._lock:
                self._error_lines.append(line.rstrip()[:500])
                self._error_lines = self._error_lines[-8:]

    def _read_samples(self) -> None:
        process = self._process
        if process is None or process.stdout is None:
            return
        for line in process.stdout:
            try:
                columns = next(csv.reader([line]))
            except (csv.Error, StopIteration):
                continue
            if len(columns) != 11:
                continue
            observation = {
                "remote_timestamp": columns[0].strip(),
                "received_at": _utc_now(),
                "offset_seconds": max(
                    0.0,
                    time.monotonic() - (self._capture_started_monotonic or time.monotonic()),
                ),
                "device": {
                    "index": _number(columns[1]),
                    "name": columns[2].strip() or None,
                    "uuid": columns[3].strip() or None,
                    "driver_version": columns[4].strip() or None,
                    "memory_used_mb": _number(columns[5]),
                    "memory_total_mb": _number(columns[6]),
                    "utilization_percent": _number(columns[7]),
                    "temperature_c": _number(columns[8]),
                    "power_draw_w": _number(columns[9]),
                    "power_limit_w": _number(columns[10]),
                },
            }
            self._record_observation(observation)
        if not self._stop_requested:
            return_code = process.poll()
            if return_code is not None:
                self._unexpected_exit = True
                with self._lock:
                    detail = "\n".join(self._error_lines).strip()
                    self._error = detail or f"Remote GPU sampler exited with status {return_code}"

    def _record_observation(self, observation: dict[str, Any]) -> None:
        if self._samples_path is None:
            return
        self._samples_path.parent.mkdir(parents=True, exist_ok=True)
        with self._samples_path.open("a", encoding="utf-8", newline="") as stream:
            stream.write(json.dumps(observation, ensure_ascii=False, allow_nan=False) + "\n")
        device = observation["device"]
        key = str(device.get("uuid") or device.get("index") or "unknown")
        with self._lock:
            summary = self._devices.setdefault(
                key,
                {
                    "index": device.get("index"),
                    "name": device.get("name"),
                    "uuid": device.get("uuid"),
                    "driver_version": device.get("driver_version"),
                    "sample_count": 0,
                    "memory_total_mb": device.get("memory_total_mb"),
                    "peak_memory_used_mb": None,
                    "average_utilization_percent": None,
                    "peak_utilization_percent": None,
                    "peak_temperature_c": None,
                    "peak_power_draw_w": None,
                    "peak_power_limit_w": None,
                    "_utilization_total": 0.0,
                    "_utilization_samples": 0,
                },
            )
            summary["sample_count"] += 1
            for source, destination in (
                ("memory_used_mb", "peak_memory_used_mb"),
                ("utilization_percent", "peak_utilization_percent"),
                ("temperature_c", "peak_temperature_c"),
                ("power_draw_w", "peak_power_draw_w"),
                ("power_limit_w", "peak_power_limit_w"),
            ):
                value = device.get(source)
                if isinstance(value, (int, float)):
                    current = summary[destination]
                    summary[destination] = value if current is None else max(current, value)
            utilization = device.get("utilization_percent")
            if isinstance(utilization, (int, float)):
                summary["_utilization_total"] += utilization
                summary["_utilization_samples"] += 1
            if summary["_utilization_samples"]:
                summary["average_utilization_percent"] = (
                    summary["_utilization_total"] / summary["_utilization_samples"]
                )
            self._sample_count += 1

    def stop(self) -> dict[str, Any]:
        """Stop the remote process and return a schema-ready per-run summary."""
        if not self.enabled:
            return self.summary()
        process = self._process
        if process is not None:
            return_code = process.poll()
            if return_code is not None and not self._stop_requested:
                self._unexpected_exit = True
                if self._error is None:
                    self._error = f"Remote GPU sampler exited with status {return_code}"
            elif return_code is None:
                self._stop_requested = True
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
        if self._reader is not None:
            self._reader.join(timeout=5)
        if self._stderr_reader is not None:
            self._stderr_reader.join(timeout=2)
        if self._capture_ended_at is None:
            self._capture_ended_at = _utc_now()
        with self._lock:
            if self._sample_count == 0 and self._error is None:
                detail = "\n".join(self._error_lines).strip()
                self._error = detail or "No nvidia-smi samples received over SSH"
            if self._error is not None and self.key_file is not None:
                self._error = self._error.replace(str(self.key_file), "<ssh-key>")
        return self.summary()

    def summary(self) -> dict[str, Any]:
        with self._lock:
            devices = []
            for raw in self._devices.values():
                devices.append(
                    {key: value for key, value in raw.items() if not key.startswith("_")}
                )
            sample_count = self._sample_count
            error = self._error
        if not self.enabled:
            status = "not_requested"
        elif sample_count == 0:
            status = (
                "connecting"
                if self._process is not None
                and self._process.poll() is None
                and not self._stop_requested
                else "unavailable"
            )
        elif self._unexpected_exit:
            status = "partial"
        else:
            status = "available"
        return {
            "status": status,
            "source": "remote_nvidia_smi_over_ssh" if self.enabled else "not_requested",
            "target": (
                {"host": self.host, "user": self.user, "port": self.port}
                if self.enabled
                else None
            ),
            "sample_interval_seconds": self.interval_seconds if self.enabled else None,
            "started_at": self._capture_started_at,
            "ended_at": self._capture_ended_at,
            "sample_count": sample_count,
            "samples_file": (
                self._samples_path.name
                if self._samples_path is not None and self._samples_path.is_file()
                else None
            ),
            "devices": devices,
            "error": error,
        }
