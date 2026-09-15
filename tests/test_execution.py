from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from runner.client import FakeModelClient, ModelResponse
from runner.config import load_benchmark_config, validate_document
from runner.discovery import discover_tasks
from runner.execution import run_one_shot
from tests.support import create_repository


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


if __name__ == "__main__":
    unittest.main()
