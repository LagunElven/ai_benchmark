from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from runner.client import FakeModelClient, ModelResponse
from runner.config import load_benchmark_config, validate_document
from runner.discovery import discover_tasks
from runner.execution import run_one_shot, run_repair
from tests.support import create_repository


class SequenceClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.calls = 0
        self.messages: list[list[dict[str, str]]] = []

    def complete(self, messages: list[dict[str, str]], *, max_output_tokens: int) -> ModelResponse:
        if self.calls >= len(self.responses):
            raise AssertionError("unexpected extra model call")
        self.messages.append(list(messages))
        response = FakeModelClient(self.responses[self.calls]).complete(
            messages, max_output_tokens=max_output_tokens
        )
        self.calls += 1
        return response


class ExecutionTests(unittest.TestCase):
    def test_one_shot_run_persists_valid_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_benchmark_config(create_repository(root))
            task = discover_tasks(config)[0]
            client = FakeModelClient('{"changes":[{"path":"app.py","content":"VALUE = 2\\n"}]}')

            result_path = run_one_shot(config, task, client)
            result = json.loads(result_path.read_text(encoding="utf-8"))

            validate_document(result, root / "schemas" / "run-result.schema.json", result_path)
            self.assertEqual(result["run"]["status"], "completed")
            self.assertTrue(result["validation"]["task_success"])
            self.assertEqual(result["patch"]["files_modified"], ["app.py"])
            self.assertEqual(result["patch"]["relevant_file_precision"], 1.0)
            self.assertTrue((root / "results" / "raw" / "runs.jsonl").is_file())
            self.assertFalse(any((root / ".benchmark-work").iterdir()))

    def test_result_records_effective_task_output_limit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_benchmark_config(create_repository(root))
            config.data["model"]["generation"]["max_output_tokens"] = 12000
            task = discover_tasks(config)[0]

            result_path = run_one_shot(
                config,
                task,
                FakeModelClient('{"changes":[{"path":"app.py","content":"VALUE = 2\\n"}]}'),
            )
            result = json.loads(result_path.read_text(encoding="utf-8"))

            self.assertEqual(result["model"]["parameters"]["max_output_tokens"], 1000)

    def test_hidden_validation_runs_in_disposable_validator_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_benchmark_config(create_repository(root, hidden_validation=True))
            task = discover_tasks(config)[0]

            result_path = run_one_shot(
                config,
                task,
                FakeModelClient('{"changes":[{"path":"app.py","content":"VALUE = 2\\n"}]}'),
            )
            result = json.loads(result_path.read_text(encoding="utf-8"))

            self.assertEqual(result["run"]["status"], "completed")
            self.assertEqual(result["validation"]["outcome"], "passed")
            self.assertTrue(result["validation"]["task_success"])
            self.assertEqual(result["validation"]["hidden"]["status"], "passed")
            self.assertEqual(result["validation"]["hidden"]["passed"], 1)
            self.assertFalse(any(root.glob(".benchmark-work/*-validator")))

    def test_model_messages_never_contain_private_material(self) -> None:
        class RecordingClient(FakeModelClient):
            def __init__(self) -> None:
                super().__init__('{"changes":[{"path":"app.py","content":"VALUE = 2\\n"}]}')
                self.messages: list[dict[str, str]] = []

            def complete(
                self, messages: list[dict[str, str]], *, max_output_tokens: int
            ) -> ModelResponse:
                self.messages = list(messages)
                return super().complete(messages, max_output_tokens=max_output_tokens)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_benchmark_config(create_repository(root, hidden_validation=True))
            task = discover_tasks(config)[0]
            client = RecordingClient()

            result_path = run_one_shot(config, task, client)
            result = json.loads(result_path.read_text(encoding="utf-8"))

            self.assertTrue(result["validation"]["task_success"])
            self.assertNotIn("secret", json.dumps(client.messages, ensure_ascii=False))

    def test_missing_private_tests_fails_closed_without_workspace_leak(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_benchmark_config(create_repository(root, hidden_validation=True))
            task = discover_tasks(config)[0]
            shutil.rmtree(root / "private-tests" / "JAVA-99")

            result_path = run_one_shot(
                config,
                task,
                FakeModelClient('{"changes":[{"path":"app.py","content":"VALUE = 2\\n"}]}'),
            )
            result = json.loads(result_path.read_text(encoding="utf-8"))

            self.assertEqual(result["run"]["status"], "failed")
            self.assertFalse(result["validation"]["task_success"])
            self.assertEqual(result["validation"]["hidden"]["status"], "failed")
            self.assertIn("private tests are missing", result["errors"][0]["message"])
            self.assertFalse(any(root.glob(".benchmark-work/*-validator")))

    def test_repair_returns_public_feedback_and_stops_after_success(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_benchmark_config(create_repository(root, hidden_validation=True))
            task = discover_tasks(config)[0]
            client = SequenceClient(
                [
                    '{"changes":[{"path":"app.py","content":"VALUE = 3\\n"}]}',
                    '{"changes":[{"path":"app.py","content":"VALUE = 2\\n"}]}',
                    '{"changes":[{"path":"app.py","content":"VALUE = 99\\n"}]}',
                ]
            )

            result_path = run_repair(config, task, client)
            result = json.loads(result_path.read_text(encoding="utf-8"))
            second_prompt = json.dumps(client.messages[1], ensure_ascii=False)

            self.assertEqual(client.calls, 2)
            self.assertEqual(result["run"]["mode"], "repair")
            self.assertEqual(result["run"]["repair_iterations"], 2)
            self.assertEqual(result["repair"]["successful_iteration"], 2)
            self.assertFalse(result["repair"]["pass_at_1"])
            self.assertTrue(result["repair"]["pass_at_2"])
            self.assertTrue(result["repair"]["pass_at_3"])
            self.assertEqual(result["validation"]["hidden"]["status"], "passed")
            self.assertIn("Public validation feedback", second_prompt)
            self.assertIn("AssertionError", second_prompt)
            self.assertNotIn("secret", second_prompt)
            self.assertEqual(len(result["artifacts"]["model_responses"]), 2)

    def test_repair_detects_repeated_failures_and_honors_three_attempt_cap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_benchmark_config(create_repository(root))
            task = discover_tasks(config)[0]
            invalid = '{"changes":[{"path":"app.py","content":"VALUE = 3\\n"}]}'
            client = SequenceClient([invalid, invalid, invalid, invalid])

            result_path = run_repair(config, task, client)
            result = json.loads(result_path.read_text(encoding="utf-8"))

            self.assertEqual(client.calls, 3)
            self.assertEqual(result["run"]["repair_iterations"], 3)
            self.assertEqual(result["validation"]["outcome"], "failed")
            self.assertFalse(result["repair"]["pass_at_1"])
            self.assertFalse(result["repair"]["pass_at_2"])
            self.assertFalse(result["repair"]["pass_at_3"])
            self.assertTrue(result["repair"]["repeated_failure_pattern"])
            self.assertEqual(result["validation"]["hidden"]["status"], "not_run")

    def test_repair_token_budget_stops_before_an_extra_call(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_benchmark_config(create_repository(root))
            config.data["runner"]["max_repair_total_output_tokens"] = 1000
            task = discover_tasks(config)[0]
            invalid = '{"changes":[{"path":"app.py","content":"VALUE = 3\\n"}]}'
            client = SequenceClient([invalid, invalid])

            result_path = run_repair(config, task, client)
            result = json.loads(result_path.read_text(encoding="utf-8"))

            self.assertEqual(client.calls, 1)
            self.assertEqual(result["run"]["repair_iterations"], 1)
            self.assertIn("token budget exhausted", result["errors"][0]["message"])


if __name__ == "__main__":
    unittest.main()
