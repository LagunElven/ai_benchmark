from __future__ import annotations

import unittest

from runner.document_metrics import (
    character_error_rate,
    edit_distance,
    score_fields,
    score_json,
    score_text,
    word_error_rate,
)


class DocumentMetricsTests(unittest.TestCase):
    def test_edit_distance_and_error_rates_are_deterministic(self) -> None:
        self.assertEqual(edit_distance(list("kitten"), list("sitting")), 3)
        self.assertAlmostEqual(character_error_rate("abc", "axc"), 1 / 3)
        self.assertAlmostEqual(word_error_rate("one two three", "one three"), 1 / 3)
        self.assertEqual(score_text("one two", "one two")["cer"], 0.0)

    def test_field_metrics_preserve_missing_and_hallucinated_fields(self) -> None:
        expected = {
            "invoice_id": "INV-1",
            "invoice_date": "2026-01-02",
            "total": 12.50,
            "line_items": [{"description": "A", "quantity": 2}],
        }
        actual = {
            "invoice_id": "INV-1",
            "invoice_date": "2026-01-03",
            "total": 12.5,
            "line_items": [{"description": "A", "quantity": 2, "extra": "x"}],
        }
        result = score_fields(expected, actual)
        self.assertEqual(result["exact_field_accuracy"], 4 / 5)
        self.assertEqual(result["numeric_field_accuracy"], 1.0)
        self.assertEqual(result["date_field_accuracy"], 0.0)
        self.assertEqual(result["identifier_field_accuracy"], 1.0)
        self.assertEqual(result["missing_fields"], [])
        self.assertEqual(result["hallucinated_fields"], ["line_items[0].extra"])
        self.assertEqual(result["table_cell_accuracy"], 1.0)

    def test_json_invalidity_is_separate_from_field_quality(self) -> None:
        result = score_json({"total": 1}, "not-json")
        self.assertFalse(result["json_validity"])
        self.assertEqual(result["exact_field_accuracy"], 0.0)

    def test_schema_validity_is_reported_separately(self) -> None:
        result = score_fields(
            {"total": 1},
            {"total": 1},
            schema={
                "type": "object",
                "required": ["total"],
                "properties": {"total": {"type": "number"}},
            },
        )
        self.assertTrue(result["json_validity"])
        self.assertTrue(result["schema_validity"])


if __name__ == "__main__":
    unittest.main()
