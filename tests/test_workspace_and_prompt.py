from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runner.config import load_benchmark_config
from runner.discovery import discover_tasks
from runner.errors import WorkspaceError
from runner.prompting import build_messages
from runner.workspace import CleanWorkspace, ValidatorWorkspace
from tests.support import create_repository


class WorkspaceAndPromptTests(unittest.TestCase):
    def test_private_tests_are_not_copied_or_prompted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_benchmark_config(create_repository(root))
            task = discover_tasks(config)[0]

            with CleanWorkspace(config, task, "safe-run") as workspace:
                self.assertTrue((workspace / "app.py").is_file())
                self.assertTrue((workspace / "public-tests" / "README.txt").is_file())
                self.assertFalse((workspace / "private-tests").exists())
                messages = build_messages(task, workspace, 100000)
                serialized = "\n".join(message["content"] for message in messages)
                self.assertNotIn("secret", serialized)
                self.assertNotIn("private-tests", serialized)
                self.assertIn("Visible public test notes", serialized)

            self.assertFalse((root / ".benchmark-work" / "safe-run").exists())

    def test_private_tests_are_only_in_validator_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_benchmark_config(create_repository(root, hidden_validation=True))
            task = discover_tasks(config)[0]

            with CleanWorkspace(config, task, "isolation-run") as model_workspace:
                with ValidatorWorkspace(
                    config, task, model_workspace, "isolation-run"
                ) as validator:
                    self.assertNotEqual(model_workspace, validator)
                    self.assertFalse((model_workspace / "answer.txt").exists())
                    self.assertEqual(
                        (validator / "answer.txt").read_text(encoding="utf-8"), "secret"
                    )
                self.assertFalse((root / ".benchmark-work" / "isolation-run-validator").exists())

    def test_hidden_file_collision_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = load_benchmark_config(create_repository(root, hidden_validation=True))
            task = discover_tasks(config)[0]
            (root / "private-tests" / "JAVA-99" / "app.py").write_text(
                "must not overwrite", encoding="utf-8"
            )

            with CleanWorkspace(config, task, "collision-run") as model_workspace:
                with (
                    self.assertRaisesRegex(WorkspaceError, "collides"),
                    ValidatorWorkspace(config, task, model_workspace, "collision-run"),
                ):
                    pass
                self.assertEqual(
                    (model_workspace / "app.py").read_text(encoding="utf-8"), "VALUE = 1\n"
                )
            self.assertFalse((root / ".benchmark-work" / "collision-run-validator").exists())


if __name__ == "__main__":
    unittest.main()
