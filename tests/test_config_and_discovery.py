from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runner.config import load_benchmark_config
from runner.discovery import discover_tasks, filter_tasks
from runner.errors import ConfigurationError
from tests.support import create_repository, write_yaml


class ConfigAndDiscoveryTests(unittest.TestCase):
    def test_discovers_and_filters_valid_task(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = load_benchmark_config(create_repository(Path(directory)))
            tasks = discover_tasks(config)

            self.assertEqual([task.id for task in tasks], ["JAVA-99"])
            self.assertEqual([task.id for task in filter_tasks(tasks, suite="smoke")], ["JAVA-99"])
            self.assertEqual(filter_tasks(tasks, tag="missing"), [])
            self.assertEqual(filter_tasks(tasks, category="spring"), [])

    def test_rejects_repository_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = create_repository(root)
            config = load_benchmark_config(config_path).data
            config["paths"]["tasks"] = "../outside"
            write_yaml(config_path, config)

            with self.assertRaisesRegex(ConfigurationError, "outside the repository"):
                load_benchmark_config(config_path)


if __name__ == "__main__":
    unittest.main()
