"""Deterministic summaries for serving request measurements."""

from __future__ import annotations

from math import ceil
from typing import Any


def percentile(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    if not 0 <= quantile <= 1:
        raise ValueError("quantile must be between zero and one")
    ordered = sorted(values)
    rank = max(0, ceil(quantile * len(ordered)) - 1)
    return ordered[rank]


def distribution(values: list[float]) -> dict[str, float | int | None]:
    return {
        "count": len(values),
        "p50": percentile(values, 0.50),
        "p95": percentile(values, 0.95),
    }


def summarize_requests(
    requests: list[dict[str, Any]], *, wall_seconds: float | None = None
) -> dict[str, Any]:
    completed = [item for item in requests if item["status"] == "completed"]
    ttft = [item["ttft_seconds"] for item in completed if item["ttft_seconds"] is not None]
    total = [item["total_seconds"] for item in completed]
    generation = [
        item["generation_seconds"]
        for item in completed
        if item["generation_seconds"] is not None
    ]
    tpot = [item["tpot_seconds"] for item in completed if item["tpot_seconds"] is not None]
    per_user = []
    for item in completed:
        if (
            item["output_tokens"]
            and item["generation_seconds"]
            and item["generation_seconds"] > 0
        ):
            per_user.append(item["output_tokens"] / item["generation_seconds"])
    output_tokens = sum(item["output_tokens"] or 0 for item in requests)
    input_tokens = sum(item["input_tokens"] or 0 for item in requests)
    effective_wall = wall_seconds
    if effective_wall is None and requests:
        effective_wall = max(item["ended_offset_seconds"] for item in requests) - min(
            item["started_offset_seconds"] for item in requests
        )
    effective_wall = max(effective_wall or 0.0, 0.0)
    failed = [item for item in requests if item["status"] != "completed"]
    oom = [item for item in requests if item["status"] == "oom"]
    timeouts = [item for item in requests if item["status"] == "timeout"]
    kv_hits = [
        item["server_metrics"]["kv_cache_hit_tokens"]
        for item in requests
        if "kv_cache_hit_tokens" in item["server_metrics"]
    ]
    kv_misses = [
        item["server_metrics"]["kv_cache_miss_tokens"]
        for item in requests
        if "kv_cache_miss_tokens" in item["server_metrics"]
    ]
    return {
        "requests_total": len(requests),
        "requests_completed": len(completed),
        "requests_failed": len(failed),
        "failure_rate": len(failed) / len(requests) if requests else 0.0,
        "timeouts": len(timeouts),
        "out_of_memory": len(oom),
        "input_tokens_total": input_tokens,
        "output_tokens_total": output_tokens,
        "ttft_seconds": distribution(ttft),
        "generation_seconds": distribution(generation),
        "total_latency_seconds": distribution(total),
        "tpot_seconds": distribution(tpot),
        "tokens_per_second_per_user": distribution(per_user),
        "aggregate_output_tokens_per_second": output_tokens / effective_wall
        if effective_wall > 0
        else None,
        "requests_per_second": len(completed) / effective_wall if effective_wall > 0 else None,
        "wall_seconds": effective_wall,
        "kv_cache": {
            "reported": bool(kv_hits or kv_misses),
            "hit_tokens_total": sum(kv_hits) if kv_hits else None,
            "miss_tokens_total": sum(kv_misses) if kv_misses else None,
            "requests_with_metrics": len(kv_hits) + len(kv_misses),
        },
    }
