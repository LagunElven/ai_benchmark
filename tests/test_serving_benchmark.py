from __future__ import annotations

import json
import re
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


class _TripledWordTokenizer:
    """Small stand-in for a subword tokenizer in context calibration tests."""

    def apply_chat_template(self, messages, *, tokenize, add_generation_prompt):
        del tokenize, add_generation_prompt
        text = " ".join(message["content"] for message in messages)
        token_count = len(re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)) * 3
        return list(range(token_count))


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

    def test_exact_tokenizer_calibrates_full_prompt_instead_of_regex_units(self) -> None:
        messages, estimated = build_messages(
            8000, "shared-prefix", 1, tokenizer=_TripledWordTokenizer()
        )
        self.assertGreaterEqual(estimated, 8000)
        self.assertLess(estimated, 8010)
        self.assertEqual(len(messages), 2)

    def test_qwen_serving_smoke_declares_exact_tokenizer(self) -> None:
        root = Path(__file__).resolve().parents[1]
        config = load_serving_config(root / "campaigns" / "gpu" / "serving-qwen-smoke.yaml")
        self.assertEqual(config.data["tokenizer"]["type"], "huggingface")
        self.assertEqual(config.data["tokenizer"]["repository"], "Qwen/Qwen3.8-27B")
        self.assertEqual(
            config.data["tokenizer"]["revision"],
            config.data["model_metadata"]["tokenizer_revision"],
        )

    def test_qwen_no_prefix_smoke_disables_prefix_caching_explicitly(self) -> None:
        root = Path(__file__).resolve().parents[1]
        config = load_serving_config(
            root / "campaigns" / "gpu" / "serving-qwen-smoke-no-prefix.yaml"
        )
        self.assertFalse(config.data["serving"]["prefix_caching"])
        self.assertIn("--no-enable-prefix-caching", config.data["serving"]["launch_command"])

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
                    "max_num_seqs": None,
                    "reasoning_parser": None,
                },
                "matrix": {
                    "concurrency": [2],
                    "context_tokens": [32],
                    "prefix_modes": ["cold", "shared-prefix"],
                    "warmup_batches": 1,
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
        progress: list[str] = []
        with tempfile.TemporaryDirectory() as directory:
            result_path = ServingBenchmark(config, directory).run(
                _FakeServingClient(), progress=progress.append
            )
            result = json.loads(result_path.read_text(encoding="utf-8"))
        self.assertFalse(list(Draft202012Validator(schema).iter_errors(result)))
        self.assertEqual(result["run"]["status"], "completed")
        self.assertEqual(result["configuration"]["tokenizer"]["method"], "fallback:regex")
        self.assertEqual(len(result["cases"]), 2)
        self.assertEqual(progress[0], "[1/2] c2-ctx32-cold started")
        self.assertIn("[2/2] c2-ctx32-shared-prefix completed", progress[-1])
        for case in result["cases"]:
            self.assertEqual(case["warmup"]["requested"], 2)
            self.assertEqual(case["warmup"]["batches_requested"], 1)
            self.assertEqual(case["warmup"]["completed"], 2)
            self.assertEqual(case["metrics"]["requests_total"], 4)
            self.assertEqual(case["metrics"]["requests_failed"], 0)
            self.assertEqual(case["resources"]["source_host_role"], "benchmark_runner")
            self.assertGreaterEqual(case["resources"]["sample_count"], 2)


if __name__ == "__main__":
    unittest.main()
