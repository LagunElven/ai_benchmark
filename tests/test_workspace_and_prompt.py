from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runner.config import load_benchmark_config
from runner.discovery import discover_tasks
from runner.prompting import build_messages
from runner.workspace import CleanWorkspace
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


if __name__ == "__main__":
    unittest.main()
