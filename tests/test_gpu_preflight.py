from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

from runner.gpu_preflight import build_preflight_manifest, load_gpu_plan


class GpuPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(__file__).resolve().parents[1]

    def test_plan_contains_gpu_campaigns_and_known_variants(self) -> None:
        plan = load_gpu_plan(self.root / "campaigns" / "gpu" / "plan.yaml")
        self.assertEqual(
            {item["id"] for item in plan["campaigns"]},
            {"C-003", "C-004", "C-005", "C-006", "C-009", "C-010", "C-011", "C-012", "C-013"},
        )
        self.assertEqual(
            {item["id"] for item in plan["model"]["artifact_variants"]},
            {"bf16", "fp8", "nvfp4"},
        )
        self.assertEqual(plan["serving"]["engine"], "vllm")
        self.assertEqual(plan["serving"]["engine_version"], "0.29.0")
        self.assertEqual(plan["serving"]["max_num_seqs"], 16)
        self.assertEqual(plan["serving"]["reasoning_parser"], "qwen3")
        self.assertEqual(
            plan["model"]["tokenizer_repository"],
            "https://huggingface.co/Qwen/Qwen3.8-27B",
        )
        self.assertEqual(
            {
                item["artifact_variant"]
                for item in plan["campaigns"]
            },
            {"bf16", "fp8", "nvfp4"},
        )
        spark_campaigns = [
            item for item in plan["campaigns"] if "DGX Spark" in item["hardware_model"]
        ]
        self.assertEqual({item["id"] for item in spark_campaigns}, {"C-009", "C-010", "C-012"})
        rtx_pro_campaigns = [
            item for item in plan["campaigns"] if "RTX PRO 6000" in item["hardware_model"]
        ]
        self.assertEqual(
            {item["id"] for item in rtx_pro_campaigns}, {"C-004", "C-006", "C-011", "C-013"}
        )
        self.assertTrue(
            all("Server Edition" in item["hardware_model"] for item in rtx_pro_campaigns)
        )
        nvfp4_campaigns = [
            item for item in plan["campaigns"] if item["artifact_variant"] == "nvfp4"
        ]
        self.assertEqual({item["id"] for item in nvfp4_campaigns}, {"C-011", "C-012"})

    def test_preflight_hashes_visible_inputs_without_private_tests(self) -> None:
        manifest = build_preflight_manifest(
            config_path=self.root / "benchmark.qwen3.8-bf16.yaml",
            serving_config_path=self.root / "campaigns" / "gpu" / "serving-qwen.yaml",
            plan_path=self.root / "campaigns" / "gpu" / "plan.yaml",
            campaign_id="C-003",
        )
        self.assertEqual(manifest["status"], "ready")
        self.assertEqual(manifest["inputs"]["visible_task_count"], 74)
        self.assertFalse(manifest["pending_decisions"])
        self.assertEqual(
            manifest["campaign"]["planned_model_source_repository"],
            "https://huggingface.co/Qwen/Qwen3.8-27B",
        )
        self.assertEqual(
            manifest["campaign"]["planned_model_revision"],
            "1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0",
        )
        self.assertNotIn("private-tests", json.dumps(manifest, ensure_ascii=False))
        self.assertTrue(
            all(
                "sha256" in task_file
                for task in manifest["inputs"]["visible_tasks"]
                for task_file in task["files"]
            )
        )

    def test_nvfp4_preflight_uses_distinct_checkpoint_metadata(self) -> None:
        manifest = build_preflight_manifest(
            config_path=self.root / "benchmark.qwen3.8-nvfp4.yaml",
            serving_config_path=self.root / "campaigns" / "gpu" / "serving-qwen-nvfp4.yaml",
            plan_path=self.root / "campaigns" / "gpu" / "plan.yaml",
            campaign_id="C-011",
        )
        self.assertEqual(manifest["status"], "ready")
        self.assertEqual(manifest["campaign"]["planned_quantization"], "NVFP4-MIXED")
        self.assertEqual(
            manifest["campaign"]["planned_model_source_repository"],
            "https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4",
        )
        self.assertEqual(
            manifest["campaign"]["planned_model_revision"],
            "dbb8f445b3145f8a4c18ddc769f032d57d32867c",
        )

    def test_qwen_quality_configs_honor_task_output_limits(self) -> None:
        for filename in (
            "benchmark.qwen3.8-bf16.yaml",
            "benchmark.qwen3.8-fp8.yaml",
            "benchmark.qwen3.8-nvfp4.yaml",
        ):
            with self.subTest(filename=filename):
                config = yaml.safe_load((self.root / filename).read_text(encoding="utf-8"))
                self.assertFalse(config["runner"]["override_task_max_output_tokens"])

    def test_no_thinking_profile_is_labeled_as_operational(self) -> None:
        plan = load_gpu_plan(self.root / "campaigns" / "gpu" / "plan.yaml")
        campaign = next(item for item in plan["campaigns"] if item["id"] == "C-013")
        self.assertEqual(campaign["comparison_type"], "operational_solution")
        self.assertEqual(campaign["artifact_variant"], "bf16")


if __name__ == "__main__":
    unittest.main()
