from __future__ import annotations

import unittest
from pathlib import Path

from runner.legacy import compare_vector_outputs, detect_toolchains, load_legacy_fixture


class LegacyFixtureTests(unittest.TestCase):
    def test_fixture_manifests_validate_and_record_source_status(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifests = sorted(root.glob("tasks/legacy/*/*/workspace/fixtures/manifest.json"))
        manifest_ids = {path.parent.parent.parent.name for path in manifests}
        self.assertEqual(
            manifest_ids, {"COBOL-02", "COBOL-05", "DELPHI-04", "WL-04", "ABAL-04"}
        )
        statuses = {load_legacy_fixture(path)["source_status"] for path in manifests}
        self.assertEqual(statuses, {"verified_syntax", "synthetic_pseudocode"})
        for path in manifests:
            fixture = load_legacy_fixture(path)
            self.assertTrue(fixture["equivalence_vectors"])

    def test_vector_comparison_reports_structured_mismatches(self) -> None:
        self.assertTrue(compare_vector_outputs(["1", "2"], ["1", "2"])["passed"])
        result = compare_vector_outputs(["1"], ["2", "3"])
        self.assertFalse(result["passed"])
        self.assertEqual([item["index"] for item in result["mismatches"]], [0, 1])

    def test_toolchain_detection_is_safe_and_explicit(self) -> None:
        detected = detect_toolchains()
        self.assertEqual(set(detected), {"gnu_cobol", "delphi", "windev", "abal"})
        self.assertIn("available", detected["gnu_cobol"])
        self.assertFalse(detected["abal"]["available"])


if __name__ == "__main__":
    unittest.main()
