from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from serving.benchmark import (
    ServingBenchmark,
    ServingConfig,
    build_messages,
    case_specs,
    load_serving_config,
)
from serving.client import StreamMeasurement


class _FakeServingClient:
    def complete_stream(self, messages, **kwargs) -> StreamMeasurement:
        del messages, kwargs
        started = time.monotonic()
        return StreamMeasurement(
            status="completed",
            started=started,
            ended=started + 0.01,
            first_token=started + 0.002,
            input_tokens=None,
            output_tokens=4,
            error_type=None,
            error_message=None,
            server_metrics={},
        )


class ServingBenchmarkTests(unittest.TestCase):
    def test_default_matrix_contains_all_required_dimensions(self) -> None:
        root = Path(__file__).resolve().parents[1]
        config = load_serving_config(root / "serving" / "config.yaml")
        specs = case_specs(config)
        self.assertEqual(len(specs), 40)
        self.assertEqual({spec.concurrency for spec in specs}, {1, 2, 5, 10})
        self.assertEqual(
            {spec.context_tokens for spec in specs}, {8000, 32000, 64000, 100000, 200000}
        )
        self.assertEqual({spec.prefix_mode for spec in specs}, {"cold", "shared-prefix"})
        self.assertEqual(len({spec.case_id for spec in specs}), len(specs))
        messages, estimated = build_messages(8000, "shared-prefix", 1)
        self.assertGreaterEqual(estimated, 8000)
        self.assertEqual(len(messages), 2)
        _, large_estimated = build_messages(200000, "cold", 2)
        self.assertGreaterEqual(large_estimated, 200000)

    def test_run_persists_schema_valid_campaign_with_injected_client(self) -> None:
        config = ServingConfig(
            path=Path(__file__).resolve().parents[1] / "serving" / "config.yaml",
            data={
                "schema_version": "1.0",
                "name": "test-serving",
                "version": "test-1",
                "endpoint": {"base_url": "http://127.0.0.1:1/v1", "api_key_env": None},
                "model": "test-model",
                "model_metadata": {
                    "revision": None,
                    "tokenizer_revision": None,
                    "quantization": None,
                    "dtype": None,
                },
                "hardware": {
                    "accelerator_model": None,
                    "gpu_count": None,
                    "gpu_memory_gb": None,
                    "driver_version": None,
                    "cuda_version": None,
                    "cpu_model": None,
                    "host_memory_gb": None,
                },
                "serving": {
                    "engine": None,
                    "engine_version": None,
                    "launch_command": None,
                    "tensor_parallel_size": None,
                    "pipeline_parallel_size": None,
                    "max_model_length": None,
                    "prefix_caching": None,
                    "batch_size": None,
                },
                "matrix": {
                    "concurrency": [2],
                    "context_tokens": [32],
                    "prefix_modes": ["cold", "shared-prefix"],
                    "warmup_requests": 1,
                    "repetitions": 2,
                },
                "request": {
                    "timeout_seconds": 5,
                    "max_output_tokens": 4,
                    "temperature": 0.0,
                    "top_p": 1.0,
                    "seed": 1,
                    "stream": True,
                },
            },
        )
        root = Path(__file__).resolve().parents[1]
        schema = json.loads(
            (root / "schemas" / "serving-campaign-result.schema.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as directory:
            result_path = ServingBenchmark(config, directory).run(_FakeServingClient())
            result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertFalse(list(Draft202012Validator(schema).iter_errors(result)))
        self.assertEqual(result["run"]["status"], "completed")
        self.assertEqual(len(result["cases"]), 2)
        for case in result["cases"]:
            self.assertEqual(case["warmup"]["completed"], 1)
            self.assertEqual(case["metrics"]["requests_total"], 4)
            self.assertEqual(case["metrics"]["requests_failed"], 0)


if __name__ == "__main__":
    unittest.main()
