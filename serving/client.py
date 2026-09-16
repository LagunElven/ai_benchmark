"""Small OpenAI-compatible streaming client used by the serving benchmark."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from runner.context_dataset import count_tokens


@dataclass(frozen=True)
class StreamMeasurement:
    status: str
    started: float
    ended: float
    first_token: float | None
    input_tokens: int | None
    output_tokens: int | None
    error_type: str | None
    error_message: str | None
    server_metrics: dict[str, int | float | str]

    @property
    def total_seconds(self) -> float:
        return max(0.0, self.ended - self.started)

    @property
    def ttft_seconds(self) -> float | None:
        if self.first_token is None:
            return None
        return max(0.0, self.first_token - self.started)

    @property
    def generation_seconds(self) -> float | None:
        if self.first_token is None:
            return None
        return max(0.0, self.ended - self.first_token)

    @property
    def tpot_seconds(self) -> float | None:
        if self.generation_seconds is None or not self.output_tokens or self.output_tokens <= 1:
            return None
        return self.generation_seconds / (self.output_tokens - 1)

    def as_dict(self, request_id: str, case_started: float) -> dict[str, Any]:
        return {
            "request_id": request_id,
            "status": self.status,
            "started_offset_seconds": max(0.0, self.started - case_started),
            "ended_offset_seconds": max(0.0, self.ended - case_started),
            "total_seconds": self.total_seconds,
            "ttft_seconds": self.ttft_seconds,
            "generation_seconds": self.generation_seconds,
            "tpot_seconds": self.tpot_seconds,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "server_metrics": self.server_metrics,
        }


def _error_kind(status: int | None, message: str) -> str:
    lowered = message.lower()
    if status in {507, 529} or any(
        marker in lowered for marker in ("out of memory", "out-of-memory", "oom", "kv cache")
    ):
        return "oom"
    if "timed out" in lowered or "timeout" in lowered:
        return "timeout"
    return "failed"


def _error_type(status: int | None, message: str) -> str:
    lowered = message.lower()
    if status in {507, 529} or any(
        marker in lowered for marker in ("out of memory", "out-of-memory", "oom", "kv cache")
    ):
        return "oom"
    if "timed out" in lowered or "timeout" in lowered:
        return "timeout"
    return "http_error" if status is not None else "request_error"


def _server_metrics(headers: Any) -> dict[str, int | float | str]:
    names = {
        "x-kv-cache-hit-tokens": "kv_cache_hit_tokens",
        "x-kv-cache-miss-tokens": "kv_cache_miss_tokens",
        "x-gpu-memory-used-mb": "gpu_memory_used_mb",
        "x-gpu-utilization-percent": "gpu_utilization_percent",
    }
    result: dict[str, int | float | str] = {}
    for header, key in names.items():
        value = headers.get(header)
        if value is None:
            continue
        try:
            result[key] = float(value) if "." in value else int(value)
        except (TypeError, ValueError):
            result[key] = str(value)
    return result


def _usage(payload: dict[str, Any]) -> tuple[int | None, int | None]:
    usage = payload.get("usage") or {}
    prompt = usage.get("prompt_tokens")
    completion = usage.get("completion_tokens")
    return (
        int(prompt) if isinstance(prompt, (int, float)) else None,
        int(completion) if isinstance(completion, (int, float)) else None,
    )


class OpenAICompatibleServingClient:
    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        timeout_seconds: float,
        api_key_env: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.api_key_env = api_key_env

    def complete_stream(
        self,
        messages: list[dict[str, str]],
        *,
        max_output_tokens: int,
        temperature: float,
        top_p: float,
        seed: int | None,
        request_id: str,
    ) -> StreamMeasurement:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_output_tokens,
            "stream": True,
            "stream_options": {"include_usage": True},
            "user": request_id,
        }
        if seed is not None:
            payload["seed"] = seed
        headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}
        if self.api_key_env and os.environ.get(self.api_key_env):
            headers["Authorization"] = f"Bearer {os.environ[self.api_key_env]}"
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        started = time.monotonic()
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                response_headers = response.headers
                content_type = response_headers.get("content-type", "")
                if "text/event-stream" in content_type:
                    return self._read_stream(response, started, request_id, response_headers)
                body = response.read().decode("utf-8")
                return self._read_json(body, started, response_headers)
        except urllib.error.HTTPError as exc:
            ended = time.monotonic()
            try:
                body = exc.read().decode("utf-8", errors="replace")
            finally:
                exc.close()
            kind = _error_kind(exc.code, body)
            return StreamMeasurement(
                status=kind,
                started=started,
                ended=ended,
                first_token=None,
                input_tokens=None,
                output_tokens=None,
                error_type=_error_type(exc.code, body),
                error_message=f"HTTP {exc.code}: {body[:500]}",
                server_metrics=_server_metrics(exc.headers),
            )
        except TimeoutError as exc:
            ended = time.monotonic()
            return StreamMeasurement(
                status="timeout",
                started=started,
                ended=ended,
                first_token=None,
                input_tokens=None,
                output_tokens=None,
                error_type="timeout",
                error_message=str(exc) or "request timed out",
                server_metrics={},
            )
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            ended = time.monotonic()
            message = str(exc)
            kind = _error_kind(None, message)
            return StreamMeasurement(
                status=kind,
                started=started,
                ended=ended,
                first_token=None,
                input_tokens=None,
                output_tokens=None,
                error_type=_error_type(None, message),
                error_message=message[:500],
                server_metrics={},
            )

    def _read_json(self, body: str, started: float, headers: Any) -> StreamMeasurement:
        ended = time.monotonic()
        payload = json.loads(body)
        input_tokens, output_tokens = _usage(payload)
        if output_tokens is None:
            content = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
            output_tokens = count_tokens(content).tokens if content else 0
        return StreamMeasurement(
            status="completed",
            started=started,
            ended=ended,
            first_token=ended,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            error_type=None,
            error_message=None,
            server_metrics=_server_metrics(headers),
        )

    def _read_stream(
        self, response: Any, started: float, request_id: str, headers: Any
    ) -> StreamMeasurement:
        del request_id
        content_parts: list[str] = []
        first_token: float | None = None
        input_tokens: int | None = None
        output_tokens: int | None = None
        try:
            for raw_line in response:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if not data or data == "[DONE]":
                    continue
                payload = json.loads(data)
                prompt_count, completion_count = _usage(payload)
                input_tokens = prompt_count if prompt_count is not None else input_tokens
                output_tokens = completion_count if completion_count is not None else output_tokens
                choices = payload.get("choices") or []
                delta = choices[0].get("delta") if choices and isinstance(choices[0], dict) else {}
                content = delta.get("content", "") if isinstance(delta, dict) else ""
                if content:
                    content_parts.append(content)
                    if first_token is None:
                        first_token = time.monotonic()
            ended = time.monotonic()
        except TimeoutError as exc:
            ended = time.monotonic()
            return StreamMeasurement(
                status="timeout",
                started=started,
                ended=ended,
                first_token=first_token,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                error_type="timeout",
                error_message=str(exc) or "stream timed out",
                server_metrics=_server_metrics(headers),
            )
        except (OSError, json.JSONDecodeError, UnicodeError) as exc:
            ended = time.monotonic()
            message = str(exc)
            kind = _error_kind(None, message)
            return StreamMeasurement(
                status=kind,
                started=started,
                ended=ended,
                first_token=first_token,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                error_type=_error_type(None, message),
                error_message=message[:500],
                server_metrics=_server_metrics(headers),
            )
        if output_tokens is None:
            output_tokens = count_tokens("".join(content_parts)).tokens if content_parts else 0
        return StreamMeasurement(
            status="completed",
            started=started,
            ended=ended,
            first_token=first_token,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            error_type=None,
            error_message=None,
            server_metrics=_server_metrics(headers),
        )
