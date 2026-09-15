from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from runner.client import FakeModelClient
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

    def test_hidden_validation_keeps_result_incomplete(self) -> None:
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

            self.assertEqual(result["run"]["status"], "incomplete")
            self.assertEqual(result["validation"]["outcome"], "public_passed")
            self.assertIsNone(result["validation"]["task_success"])
            self.assertEqual(result["validation"]["hidden"]["status"], "not_run")


if __name__ == "__main__":
    unittest.main()
