"""Concurrent, engine-neutral serving benchmark orchestration."""

from __future__ import annotations

import hashlib
import itertools
import json
import subprocess
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

from runner.config import load_structured_file, validate_document
from runner.context_dataset import count_tokens
from serving.client import OpenAICompatibleServingClient, StreamMeasurement
from serving.metrics import summarize_requests
from serving.resources import json_safe, resource_summary, sample_resources


@dataclass(frozen=True)
class ServingConfig:
    path: Path
    data: dict[str, Any]


@dataclass(frozen=True)
class CaseSpec:
    case_id: str
    concurrency: int
    context_tokens: int
    prefix_mode: str
    warmup_requests: int
    repetitions: int


class ServingClient(Protocol):
    def complete_stream(
        self,
        messages: list[dict[str, str]],
        *,
        max_output_tokens: int,
        temperature: float,
        top_p: float,
        seed: int | None,
        request_id: str,
    ) -> StreamMeasurement: ...


def load_serving_config(path: str | Path) -> ServingConfig:
    config_path = Path(path).resolve()
    data = load_structured_file(config_path)
    schema_path = Path(__file__).resolve().parents[1] / "schemas" / "serving-config.schema.json"
    validate_document(data, schema_path, config_path)
    return ServingConfig(path=config_path, data=data)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _git_commit(root: Path) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return completed.stdout.strip() or None


def _config_hash(data: dict[str, Any]) -> str:
    serialized = json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def _fill_context(target_tokens: int, prefix: str) -> str:
    text = prefix
    filler = " repository_context_token"
    current_tokens = count_tokens(text).tokens
    filler_tokens = max(1, count_tokens(filler).tokens)
    repetitions = max(0, (target_tokens - current_tokens) // filler_tokens)
    text += filler * repetitions
    while count_tokens(text).tokens < target_tokens:
        text += filler
    return text


def build_messages(
    context_tokens: int, prefix_mode: str, request_index: int
) -> tuple[list[dict[str, str]], int]:
    """Build deterministic prompts with a shared prefix or distinct cold context."""
    system = "You are measuring serving performance. Return a short deterministic acknowledgement."
    common_prefix = (
        "Enterprise repository context begins. The following material is intentionally "
        "synthetic and is used only to control the input size."
    )
    suffix = (
        f"\nThe request-specific operation is benchmark request {request_index}. "
        "Acknowledge the operation without reproducing the context."
    )
    if prefix_mode == "shared-prefix":
        user = _fill_context(max(1, context_tokens - count_tokens(suffix).tokens), common_prefix)
        user += suffix
    elif prefix_mode == "cold":
        nonce = f"Cold-prefix nonce {request_index}. "
        remaining = max(1, context_tokens - count_tokens(nonce + suffix).tokens)
        user = nonce + _fill_context(remaining, common_prefix)
        user += suffix
    else:
        raise ValueError(f"Unsupported prefix mode: {prefix_mode}")
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    estimated = sum(count_tokens(message["content"]).tokens for message in messages)
    return messages, estimated


def case_specs(config: ServingConfig) -> list[CaseSpec]:
    matrix = config.data["matrix"]
    return [
        CaseSpec(
            case_id=f"c{concurrency}-ctx{context_tokens}-{prefix_mode}",
            concurrency=concurrency,
            context_tokens=context_tokens,
            prefix_mode=prefix_mode,
            warmup_requests=matrix["warmup_requests"],
            repetitions=matrix["repetitions"],
        )
        for concurrency, context_tokens, prefix_mode in itertools.product(
            matrix["concurrency"], matrix["context_tokens"], matrix["prefix_modes"]
        )
    ]


class ServingBenchmark:
    def __init__(self, config: ServingConfig, output_dir: str | Path) -> None:
        self.config = config
        self.output_dir = Path(output_dir).resolve()

    def plan(self) -> list[dict[str, Any]]:
        return [
            {
                "case_id": spec.case_id,
                "concurrency": spec.concurrency,
                "context_tokens": spec.context_tokens,
                "prefix_mode": spec.prefix_mode,
                "warmup_requests": spec.warmup_requests,
                "repetitions": spec.repetitions,
            }
            for spec in case_specs(self.config)
        ]

    def run(self, client: ServingClient | None = None) -> Path:
        data = self.config.data
        endpoint = data["endpoint"]
        request_config = data["request"]
        model_client = client or OpenAICompatibleServingClient(
            endpoint["base_url"],
            data["model"],
            timeout_seconds=request_config["timeout_seconds"],
            api_key_env=endpoint.get("api_key_env"),
            chat_template_kwargs=request_config.get("chat_template_kwargs"),
        )
        run_id = f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%S.%fZ')}-serving-{uuid.uuid4().hex[:8]}"
        started_at = _utc_now()
        cases: list[dict[str, Any]] = []
        for spec in case_specs(self.config):
            cases.append(self._run_case(spec, model_client))
        ended_at = _utc_now()
        has_failures = any(case["metrics"]["requests_failed"] for case in cases)
        result = {
            "schema_version": "1.0",
            "benchmark": {
                "name": "enterprise-llm-bench-serving",
                "version": data["version"],
                "git_commit": _git_commit(self.config.path.parent),
            },
            "run": {
                "id": run_id,
                "timestamp": started_at,
                "started_at": started_at,
                "ended_at": ended_at,
                "status": "completed_with_failures" if has_failures else "completed",
            },
            "configuration": {
                "name": data["name"],
                "version": data["version"],
                "sha256": _config_hash(data),
                "endpoint": {
                    "base_url": endpoint["base_url"],
                    "api_key_env": endpoint.get("api_key_env"),
                },
                "model": data["model"],
                "model_metadata": data["model_metadata"],
                "hardware": data["hardware"],
                "serving": data["serving"],
                "matrix": data["matrix"],
                "request": data["request"],
            },
            "cases": cases,
        }
        result = json_safe(result)
        run_directory = self.output_dir / run_id
        run_directory.mkdir(parents=True, exist_ok=False)
        result_path = run_directory / "campaign.json"
        schema_path = (
            Path(__file__).resolve().parents[1]
            / "schemas"
            / "serving-campaign-result.schema.json"
        )
        validate_document(result, schema_path, result_path)
        result_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="",
        )
        index_path = self.output_dir / "campaigns.jsonl"
        with index_path.open("a", encoding="utf-8", newline="") as index:
            index.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return result_path

    def _run_case(self, spec: CaseSpec, client: ServingClient) -> dict[str, Any]:
        before = sample_resources()
        case_started = time.monotonic()
        warmup_completed = 0
        warmup_failed = 0
        for warmup_index in range(spec.warmup_requests):
            measurement = self._request(client, spec, -(warmup_index + 1))
            if measurement.status == "completed":
                warmup_completed += 1
            else:
                warmup_failed += 1
        request_started = time.monotonic()
        requests: list[dict[str, Any]] = []
        for repetition in range(spec.repetitions):
            requests.extend(
                self._run_batch(
                    client,
                    spec,
                    repetition,
                    request_started,
                    case_started,
                )
            )
        request_wall = time.monotonic() - request_started
        after = sample_resources()
        return {
            "case_id": spec.case_id,
            "concurrency": spec.concurrency,
            "context_tokens": spec.context_tokens,
            "prefix_mode": spec.prefix_mode,
            "warmup": {
                "requested": spec.warmup_requests,
                "completed": warmup_completed,
                "failed": warmup_failed,
            },
            "requests": sorted(requests, key=lambda item: item["request_id"]),
            "metrics": summarize_requests(requests, wall_seconds=request_wall),
            "resources": resource_summary(before, after),
        }

    def _run_batch(
        self,
        client: ServingClient,
        spec: CaseSpec,
        repetition: int,
        request_started: float,
        case_started: float,
    ) -> list[dict[str, Any]]:
        requests: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=spec.concurrency) as executor:
            futures = {
                executor.submit(
                    self._request,
                    client,
                    spec,
                    repetition * spec.concurrency + user_index,
                ): user_index
                for user_index in range(spec.concurrency)
            }
            for future in as_completed(futures):
                user_index = futures[future]
                request_id = f"{spec.case_id}-r{repetition + 1}-u{user_index + 1}"
                try:
                    measurement = future.result()
                except Exception as exc:  # defensive containment for custom clients
                    now = time.monotonic()
                    measurement = StreamMeasurement(
                        status="failed",
                        started=now,
                        ended=now,
                        first_token=None,
                        input_tokens=None,
                        output_tokens=None,
                        error_type=type(exc).__name__,
                        error_message=str(exc)[:500],
                        server_metrics={},
                    )
                requests.append(measurement.as_dict(request_id, case_started))
        del request_started
        return requests

    def _request(
        self, client: ServingClient, spec: CaseSpec, request_index: int
    ) -> StreamMeasurement:
        messages, estimated_input_tokens = build_messages(
            spec.context_tokens, spec.prefix_mode, request_index
        )
        measurement = client.complete_stream(
            messages,
            max_output_tokens=self.config.data["request"]["max_output_tokens"],
            temperature=self.config.data["request"]["temperature"],
            top_p=self.config.data["request"]["top_p"],
            seed=self.config.data["request"]["seed"],
            request_id=f"{spec.case_id}-request-{request_index}",
        )
        if measurement.input_tokens is not None or estimated_input_tokens is None:
            return measurement
        return StreamMeasurement(
            status=measurement.status,
            started=measurement.started,
            ended=measurement.ended,
            first_token=measurement.first_token,
            input_tokens=estimated_input_tokens,
            output_tokens=measurement.output_tokens,
            error_type=measurement.error_type,
            error_message=measurement.error_message,
            server_metrics=measurement.server_metrics,
        )
