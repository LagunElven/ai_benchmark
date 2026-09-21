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
from scripts.run_quality_campaign import _find_resume_source, _sha256
from tests.support import create_repository


class QualityCampaignResumeTests(unittest.TestCase):
    def test_resume_reconstructs_campaign_without_global_checkpoint(self) -> None:
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
            run_index = root / "results" / "raw" / "runs.jsonl"
            run_index.parent.mkdir(parents=True)
            generation = {
                key: value
                for key, value in config.data["model"]["generation"].items()
                if key != "max_output_tokens"
            }
            historical_run = {
                "benchmark": config.data["benchmark"],
                "model": {
                    key: config.data["model"].get(key)
                    for key in (
                        "provider",
                        "name",
                        "revision",
                        "tokenizer_revision",
                        "quantization",
                        "dtype",
                    )
                }
                | {"parameters": generation},
                "environment": {
                    "hardware": config.data["hardware"],
                    "serving": config.data["serving"],
                },
                "run": {"mode": "one-shot", "status": "completed"},
                "task": {"id": tasks[0].id},
                "validation": {"outcome": "passed"},
                "artifacts": {"result": "results/raw/legacy-result.json"},
                "errors": [],
                "timing": {
                    "started_at": "2026-09-21T08:00:00Z",
                    "ended_at": "2026-09-21T08:00:01Z",
                },
            }
            run_index.write_text(
                json.dumps(historical_run) + "\n",
                encoding="utf-8",
            )
            source = _find_resume_source(
                config.root,
                config=config,
                campaign_id="C-003",
                mode="one-shot",
                suite="smoke",
                category=None,
                config_path=config_path.resolve(),
                config_sha256=_sha256(config_path),
                task_ids=[task.id for task in tasks],
            )

            self.assertIsNotNone(source)
            assert source is not None
            self.assertEqual(source[0].resolve(), run_index.resolve())
            self.assertEqual(source[1]["status"], "interrupted")
            self.assertEqual(len(source[1]["runs"]), 1)

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
            expected_task_ids = [task.id for task in discover_tasks(config)]
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
            self.assertTrue(completed["campaign"]["resumed_from"].endswith("campaign-progress.json"))
            index_lines = (campaign_root / "campaigns.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
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
