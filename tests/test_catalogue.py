from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runner.catalogue import catalogue_coverage, load_catalogue
from runner.errors import ConfigurationError


class CatalogueTests(unittest.TestCase):
    def test_repository_catalogue_has_target_and_implemented_coverage(self) -> None:
        root = Path(__file__).resolve().parents[1]
        catalogue = load_catalogue(root / "catalogue.yaml")
        self.assertEqual(sum(category["target"] for category in catalogue["categories"]), 74)
        summary = catalogue_coverage(root)
        self.assertEqual(summary["target_tasks"], 74)
        self.assertEqual(summary["implemented_tasks"], 72)
        self.assertEqual(summary["missing_implemented"], [])
        self.assertEqual(summary["category_mismatches"], [])
        self.assertEqual(summary["missing_validation"], [])
        self.assertEqual(summary["unexpected_tasks"], [])

    def test_catalogue_rejects_target_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalogue.yaml"
            path.write_text(
                "schema_version: '1.0'\ncategories:\n"
                "  - id: java\n    target: 2\n    tasks:\n"
                "      - {id: JAVA-99, name: test, status: planned}\n",
                encoding="utf-8",
            )
            with self.assertRaises(ConfigurationError):
                load_catalogue(path)


if __name__ == "__main__":
    unittest.main()
