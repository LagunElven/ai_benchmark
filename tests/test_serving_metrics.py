from __future__ import annotations

import unittest

from serving.metrics import percentile, summarize_requests


def request(
    request_id: str,
    status: str,
    *,
    ttft: float | None = None,
    generation: float | None = None,
    output_tokens: int | None = None,
    start: float = 0.0,
    end: float = 1.0,
    server_metrics: dict[str, int] | None = None,
) -> dict[str, object]:
    return {
        "request_id": request_id,
        "status": status,
        "started_offset_seconds": start,
        "ended_offset_seconds": end,
        "total_seconds": end - start,
        "ttft_seconds": ttft,
        "generation_seconds": generation,
        "tpot_seconds": generation / (output_tokens - 1)
        if generation is not None and output_tokens and output_tokens > 1
        else None,
        "input_tokens": 10,
        "output_tokens": output_tokens,
        "error_type": None if status == "completed" else status,
        "error_message": None,
        "server_metrics": server_metrics or {},
    }


class ServingMetricsTests(unittest.TestCase):
    def test_percentile_uses_deterministic_nearest_rank(self) -> None:
        self.assertEqual(percentile([3.0, 1.0, 2.0], 0.5), 2.0)
        self.assertEqual(percentile([3.0, 1.0, 2.0], 0.95), 3.0)
        self.assertIsNone(percentile([], 0.5))
        with self.assertRaises(ValueError):
            percentile([1.0], 1.1)

    def test_summary_separates_latency_throughput_and_failures(self) -> None:
        requests = [
            request(
                "one",
                "completed",
                ttft=0.1,
                generation=0.9,
                output_tokens=10,
                end=1.0,
                server_metrics={"kv_cache_hit_tokens": 8},
            ),
            request(
                "two",
                "completed",
                ttft=0.2,
                generation=1.8,
                output_tokens=20,
                start=0.1,
                end=2.0,
                server_metrics={"kv_cache_miss_tokens": 12},
            ),
            request("three", "timeout", start=0.2, end=2.0),
            request("four", "oom", start=0.2, end=2.0),
        ]
        summary = summarize_requests(requests, wall_seconds=2.0)
        self.assertEqual(summary["requests_total"], 4)
        self.assertEqual(summary["requests_completed"], 2)
        self.assertEqual(summary["requests_failed"], 2)
        self.assertEqual(summary["timeouts"], 1)
        self.assertEqual(summary["out_of_memory"], 1)
        self.assertEqual(summary["output_tokens_total"], 30)
        self.assertEqual(summary["ttft_seconds"]["p50"], 0.1)
        self.assertEqual(summary["total_latency_seconds"]["p95"], 1.9)
        self.assertEqual(summary["aggregate_output_tokens_per_second"], 15.0)
        self.assertEqual(summary["kv_cache"]["hit_tokens_total"], 8)
        self.assertEqual(summary["kv_cache"]["miss_tokens_total"], 12)


if __name__ == "__main__":
    unittest.main()
