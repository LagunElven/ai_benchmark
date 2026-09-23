from __future__ import annotations

import json
import shutil
import threading
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from runner.client import ModelResponse
from runner.cohort import run_closed_cohort
from runner.config import BenchmarkConfig, load_benchmark_config, validate_document
from runner.discovery import discover_tasks
from runner.errors import ConfigurationError
from scripts.run_cohort_pilot import (
    _campaign_document,
    _persist_campaign,
    _utc_now,
    _validate_agent_count,
)
from tests.support import create_repository


class _BarrierModelClient:
    def __init__(self) -> None:
        self._barrier = threading.Barrier(2)
        self._lock = threading.Lock()
        self._calls = 0

    def complete(self, messages, *, max_output_tokens):
        del messages, max_output_tokens
        with self._lock:
            self._calls += 1
            call_number = self._calls
        if call_number <= 2:
            self._barrier.wait(timeout=5)
        content = '{"changes":[{"path":"app.py","content":"VALUE = 2\\n"}]}'
        return ModelResponse(
            content=content,
            raw={},
            usage={
                "input_tokens": 10,
                "cached_input_tokens": None,
                "output_tokens": 12,
                "reasoning_tokens": 4,
            },
            generation_seconds=0.01,
        )


class CohortPilotTests(unittest.TestCase):
    def test_custom_agent_counts_are_allowed_within_task_and_server_limits(self) -> None:
        for agents in (6, 8):
            with self.subTest(agents=agents):
                _validate_agent_count(agents, task_count=18, max_num_seqs=16)

    def test_agent_count_must_be_positive_and_within_both_limits(self) -> None:
        invalid_counts = (
            (0, 18, 16, "at least 1"),
            (17, 16, 32, "distinct pilot tasks"),
            (17, 18, 16, "serving.max_num_seqs"),
        )
        for agents, task_count, max_num_seqs, message in invalid_counts:
            with (
                self.subTest(agents=agents, task_count=task_count, max_num_seqs=max_num_seqs),
                self.assertRaisesRegex(ConfigurationError, message),
            ):
                _validate_agent_count(
                    agents,
                    task_count=task_count,
                    max_num_seqs=max_num_seqs,
                )

    def test_closed_cohort_reuses_quality_runner_and_records_real_request_overlap(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = create_repository(root)
            second_task_dir = root / "tasks" / "java" / "JAVA-98"
            third_task_dir = root / "tasks" / "java" / "JAVA-97"
            shutil.copytree(root / "tasks" / "java" / "JAVA-99", second_task_dir)
            shutil.copytree(root / "tasks" / "java" / "JAVA-99", third_task_dir)
            for task_dir, task_id in (
                (second_task_dir, "JAVA-98"),
                (third_task_dir, "JAVA-97"),
            ):
                task_yaml = task_dir / "task.yaml"
                task_yaml.write_text(
                    task_yaml.read_text(encoding="utf-8").replace("JAVA-99", task_id),
                    encoding="utf-8",
                )

            config = load_benchmark_config(config_path)
            tasks = discover_tasks(config)
            selected = [task for task in tasks if task.id in {"JAVA-99", "JAVA-98", "JAVA-97"}]
            data = deepcopy(config.data)
            data["serving"]["concurrency"] = 2
            effective_config = BenchmarkConfig(config.root, config.path, data)
            result = run_closed_cohort(
                effective_config,
                selected,
                agents=2,
                mode="repair",
                client=_BarrierModelClient(),
            )

            self.assertEqual(len(result.tasks), 3)
            self.assertTrue(all(task["task_success"] for task in result.tasks))
            self.assertEqual(result.max_active_agents, 2)
            self.assertEqual(result.max_concurrent_model_requests, 2)
            self.assertEqual(len(result.model_requests), 3)
            self.assertEqual(sum(task["model_calls"] for task in result.tasks), 3)
            run_lines = (root / "results" / "raw" / "runs.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            self.assertEqual(len(run_lines), 3)
            self.assertTrue(
                all(
                    json.loads(line)["environment"]["serving"]["concurrency"] == 2
                    for line in run_lines
                )
            )

    def test_campaign_output_is_schema_valid_and_indexed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = create_repository(root)
            task_dir = root / "tasks" / "java" / "JAVA-98"
            shutil.copytree(root / "tasks" / "java" / "JAVA-99", task_dir)
            task_yaml = task_dir / "task.yaml"
            task_yaml.write_text(
                task_yaml.read_text(encoding="utf-8").replace("JAVA-99", "JAVA-98"),
                encoding="utf-8",
            )
            config = load_benchmark_config(config_path)
            tasks = [task for task in discover_tasks(config) if task.id in {"JAVA-99", "JAVA-98"}]
            plan_path = root / "cohort-plan.yaml"
            plan_path.write_text(
                "\n".join(
                    [
                        "name: test-cohort",
                        "version: '0.1'",
                        "mode: repair",
                        "agent_counts: [1, 2]",
                        "tasks: [JAVA-99, JAVA-98]",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            plan = {
                "name": "test-cohort",
                "version": "0.1",
                "mode": "repair",
                "agent_counts": [1, 2],
                "tasks": ["JAVA-99", "JAVA-98"],
            }
            data = deepcopy(config.data)
            data["serving"]["concurrency"] = 2
            effective_config = BenchmarkConfig(config.root, config.path, data)
            result = run_closed_cohort(
                effective_config,
                tasks,
                agents=2,
                mode="repair",
                client=_BarrierModelClient(),
            )
            campaign = _campaign_document(
                config=effective_config,
                plan=plan,
                plan_path=plan_path,
                benchmark_config_path=config_path,
                tasks=tasks,
                agents=2,
                started_at=_utc_now(),
                ended_at=_utc_now(),
                result=result,
                git_commit=None,
                working_tree_dirty=None,
            )
            validate_document(
                campaign,
                config.schema_dir / "cohort-pilot-result.schema.json",
                root / "campaign.json",
            )
            result_path = _persist_campaign(effective_config, campaign)
            self.assertTrue(result_path.is_file())
            index_path = root / "results" / "raw" / "cohort" / "campaigns.jsonl"
            indexed = json.loads(index_path.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(indexed["campaign"]["agent_count"], 2)
            self.assertEqual(indexed["summary"]["tasks_succeeded"], 2)


if __name__ == "__main__":
    unittest.main()
