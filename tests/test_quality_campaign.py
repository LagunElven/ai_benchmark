from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runner.client import FakeModelClient
from runner.config import load_benchmark_config
from runner.discovery import discover_tasks
from runner.execution import run_one_shot as execute_one_shot
from scripts import run_quality_campaign as campaign_script
from scripts.run_quality_campaign import (
    _campaign_result,
    _campaign_run_entry,
    _find_resume_source,
    _sha256,
)
from tests.support import create_repository


class QualityCampaignResumeTests(unittest.TestCase):
    def test_campaign_counts_errors_from_individual_run_results(self) -> None:
        run = _campaign_run_entry(
            {
                "task": {"id": "DOC-02"},
                "run": {"status": "completed"},
                "validation": {"outcome": "failed"},
                "artifacts": {"result": "results/raw/doc-02/result.json"},
                "errors": [
                    {"type": "ChangeProtocolError", "message": "invalid changes"},
                    {"type": "ModelClientError", "message": "temporary failure"},
                ],
            }
        )
        self.assertIsNotNone(run)
        assert run is not None
        campaign = _campaign_result(
            metadata={"id": "C-003"},
            started_at="2026-09-22T08:00:00Z",
            ended_at="2026-09-22T08:00:01Z",
            status="completed_with_failures",
            runs=[run],
            tasks_total=1,
        )

        self.assertEqual(campaign["summary"]["tasks_with_errors"], 1)
        self.assertEqual(
            campaign["summary"]["error_counts"],
            {"ChangeProtocolError": 1, "ModelClientError": 1},
        )

    def test_campaign_summary_separates_capacity_from_quality_failures(self) -> None:
        run = _campaign_run_entry(
            {
                "task": {"id": "CTX-06"},
                "run": {"status": "failed"},
                "validation": {"outcome": "failed"},
                "artifacts": {"result": "results/raw/ctx06/result.json"},
                "errors": [
                    {
                        "type": "ContextCapacityError",
                        "message": "Serialized prompt exceeds configured context window",
                    }
                ],
            }
        )
        assert run is not None
        campaign = _campaign_result(
            metadata={"id": "C-003"},
            started_at="2026-09-22T08:00:00Z",
            ended_at="2026-09-22T08:00:01Z",
            status="completed_with_failures",
            runs=[run],
            tasks_total=1,
        )
        self.assertEqual(campaign["summary"]["tasks_capacity_rejections"], 1)
        self.assertEqual(campaign["summary"]["tasks_quality_evaluated"], 0)
        self.assertIsNone(campaign["summary"]["quality_success_rate"])

    def test_resume_refuses_unfingerprinted_legacy_runs_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = create_repository(root)
            config = load_benchmark_config(config_path)
            tasks = discover_tasks(config)
            run_index = root / "results" / "raw" / "runs.jsonl"
            run_index.parent.mkdir(parents=True)
            run_index.write_text(json.dumps({"legacy": True}) + "\n", encoding="utf-8")
            plan_path = Path(__file__).resolve().parents[1] / "campaigns" / "gpu" / "plan.yaml"
            source = _find_resume_source(
                config.root,
                campaign_id="C-003",
                mode="one-shot",
                suite="smoke",
                category=None,
                config_path=config_path.resolve(),
                config_sha256=_sha256(config_path),
                plan_path=plan_path,
                plan_sha256=_sha256(plan_path),
                comparison_type="controlled_hardware",
                comparison_group="hardware-bf16",
                artifact_variant="bf16",
                git_commit=None,
                input_fingerprint_sha256="0" * 64,
                seed=42,
                task_revisions={task.id: task.data["revision"] for task in tasks},
                task_ids=[task.id for task in tasks],
            )
            self.assertIsNone(source)

    def test_resume_continues_from_checkpoint_without_rerunning_completed_tasks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = create_repository(root)
            second_task = root / "tasks" / "java" / "JAVA-98"
            shutil.copytree(root / "tasks" / "java" / "JAVA-99", second_task)
            task_yaml = second_task / "task.yaml"
            task_yaml.write_text(
                task_yaml.read_text(encoding="utf-8").replace("JAVA-99", "JAVA-98"),
                encoding="utf-8",
            )
            config = load_benchmark_config(config_path)
            tasks = discover_tasks(config)
            expected_task_ids = [task.id for task in tasks]
            plan_path = Path(__file__).resolve().parents[1] / "campaigns" / "gpu" / "plan.yaml"
            response = '{"changes":[{"path":"app.py","content":"VALUE = 2\\n"}]}'

            first_calls: list[str] = []

            def interrupt_after_one(config, task):
                first_calls.append(task.id)
                if len(first_calls) == 2:
                    raise KeyboardInterrupt
                return execute_one_shot(config, task, FakeModelClient(response))

            with patch.object(campaign_script, "run_one_shot", side_effect=interrupt_after_one):
                initial_status = campaign_script.main(
                    [
                        "--campaign-id",
                        "C-003",
                        "--config",
                        str(config_path),
                        "--plan",
                        str(plan_path),
                        "--mode",
                        "one-shot",
                        "--suite",
                        "smoke",
                    ]
                )

            self.assertEqual(initial_status, 130)
            self.assertEqual(first_calls, expected_task_ids)
            campaign_root = root / "results" / "raw" / "campaigns"
            initial_progress = list(campaign_root.glob("*/campaign-progress.json"))
            self.assertEqual(len(initial_progress), 1)
            interrupted = json.loads(initial_progress[0].read_text(encoding="utf-8"))
            self.assertEqual(interrupted["status"], "interrupted")
            self.assertEqual(
                [run["task_id"] for run in interrupted["runs"]], [expected_task_ids[0]]
            )

            first_prompt = tasks[0].prompt_path
            original_prompt = first_prompt.read_text(encoding="utf-8")
            first_prompt.write_text(
                original_prompt + "\nchanged during interruption\n", encoding="utf-8"
            )
            with self.assertRaises(SystemExit) as changed_error:
                campaign_script.main(
                    [
                        "--campaign-id",
                        "C-003",
                        "--config",
                        str(config_path),
                        "--plan",
                        str(plan_path),
                        "--mode",
                        "one-shot",
                        "--suite",
                        "smoke",
                        "--resume",
                    ]
                )
            self.assertEqual(changed_error.exception.code, 2)
            first_prompt.write_text(original_prompt, encoding="utf-8")

            with self.assertRaises(SystemExit) as seed_error:
                campaign_script.main(
                    [
                        "--campaign-id",
                        "C-003",
                        "--config",
                        str(config_path),
                        "--plan",
                        str(plan_path),
                        "--mode",
                        "one-shot",
                        "--suite",
                        "smoke",
                        "--seed",
                        "2",
                        "--resume",
                    ]
                )
            self.assertEqual(seed_error.exception.code, 2)

            resumed_calls: list[str] = []

            def complete_resume(config, task):
                resumed_calls.append(task.id)
                return execute_one_shot(config, task, FakeModelClient(response))

            with patch.object(campaign_script, "run_one_shot", side_effect=complete_resume):
                resumed_status = campaign_script.main(
                    [
                        "--campaign-id",
                        "C-003",
                        "--config",
                        str(config_path),
                        "--plan",
                        str(plan_path),
                        "--mode",
                        "one-shot",
                        "--suite",
                        "smoke",
                        "--resume",
                    ]
                )

            self.assertEqual(resumed_status, 0)
            self.assertEqual(resumed_calls, [expected_task_ids[1]])
            campaign_results = list(campaign_root.glob("*/campaign.json"))
            self.assertEqual(len(campaign_results), 1)
            completed = json.loads(campaign_results[0].read_text(encoding="utf-8"))
            self.assertEqual(completed["status"], "completed")
            self.assertEqual(completed["summary"]["tasks_total"], 2)
            self.assertEqual(len(completed["runs"]), 2)
            self.assertEqual(completed["campaign"]["comparison_type"], "controlled_hardware")
            self.assertEqual(completed["campaign"]["seed"], 1)
            self.assertEqual(completed["campaign"]["task_revisions"]["JAVA-98"], 1)
            self.assertEqual(len(completed["campaign"]["input_fingerprint_sha256"]), 64)
            self.assertTrue(
                completed["campaign"]["resumed_from"].endswith("campaign-progress.json")
            )
            index_lines = (
                (campaign_root / "campaigns.jsonl").read_text(encoding="utf-8").splitlines()
            )
            self.assertEqual(len(index_lines), 1)

            with self.assertRaises(SystemExit) as error:
                campaign_script.main(
                    [
                        "--campaign-id",
                        "C-003",
                        "--config",
                        str(config_path),
                        "--plan",
                        str(plan_path),
                        "--mode",
                        "one-shot",
                        "--suite",
                        "smoke",
                        "--resume",
                    ]
                )
            self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
