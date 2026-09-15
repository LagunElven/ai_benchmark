from __future__ import annotations

import json
import unittest
from pathlib import Path

from runner.config import load_benchmark_config
from runner.discovery import discover_tasks, filter_tasks


class SmokeCatalogueTests(unittest.TestCase):
    def test_representative_smoke_tasks_have_adapter_fixtures(self) -> None:
        root = Path(__file__).resolve().parents[1]
        config = load_benchmark_config(root / "benchmark.yaml")
        tasks = filter_tasks(discover_tasks(config), suite="smoke")
        expected = {"JAVA-03", "SPRING-05", "AXON-02", "WEB-03", "COBOL-05", "DOC-10", "CTX-01"}
        self.assertEqual({task.id for task in tasks}, expected)
        for task in tasks:
            fixture = root / "tests" / "fixtures" / "smoke-responses" / f"{task.id}.json"
            self.assertTrue(fixture.is_file())
            self.assertTrue((root / "private-tests" / task.id).is_dir())
            self.assertIn("smoke", task.data["suites"])

    def test_smoke_response_fixtures_use_change_protocol(self) -> None:
        root = Path(__file__).resolve().parents[1]
        for path in sorted((root / "tests" / "fixtures" / "smoke-responses").glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(set(payload), {"changes"})
            self.assertTrue(payload["changes"])


if __name__ == "__main__":
    unittest.main()
