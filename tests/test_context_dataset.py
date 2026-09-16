from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from runner.context_dataset import (
    count_tokens,
    generate_context_variants,
    score_relevant_files,
)


class ContextDatasetTests(unittest.TestCase):
    def test_materialized_quality_variants_are_versioned_and_comparable(self) -> None:
        root = Path(__file__).resolve().parents[1]
        schema = json.loads(
            (root / "schemas" / "context-variant.schema.json").read_text(encoding="utf-8")
        )
        source_path = root / "tasks" / "context" / "CTX-01" / "workspace" / "src" / "billing.py"
        source = source_path.read_text(encoding="utf-8")
        targets = {
            "CTX-02": 30000,
            "CTX-03": 60000,
            "CTX-04": 100000,
            "CTX-05": 150000,
            "CTX-06": 200000,
        }
        actual_tokens = []
        for task_id, target in targets.items():
            workspace = root / "tasks" / "context" / task_id / "workspace"
            manifest = json.loads(
                (workspace / "context-manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["target_tokens"], target)
            self.assertGreaterEqual(manifest["actual_tokens"], target)
            self.assertEqual(manifest["relevant_files"], ["src/billing.py"])
            self.assertEqual(
                manifest["source"], "tasks/context/CTX-01/workspace"
            )
            self.assertFalse(list(Draft202012Validator(schema).iter_errors(manifest)))
            self.assertEqual(
                (workspace / "src" / "billing.py").read_text(encoding="utf-8"), source
            )
            self.assertTrue((workspace / "generated-distractors").is_dir())
            actual_tokens.append(manifest["actual_tokens"])
        self.assertEqual(actual_tokens, sorted(actual_tokens))

    def test_variants_reach_targets_and_validate_manifests(self) -> None:
        root = Path(__file__).resolve().parents[1]
        schema = json.loads(
            (root / "schemas" / "context-variant.schema.json").read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            (source / "src").mkdir(parents=True)
            (source / "src" / "relevant.py").write_text("VALUE = 1\n", encoding="utf-8")
            (source / "README.md").write_text("unrelated context\n", encoding="utf-8")
            output = Path(directory) / "variants"
            variants = generate_context_variants(
                source,
                output,
                [100, 1000],
                relevant_files=["src/relevant.py"],
                seed=5,
            )
            self.assertEqual([variant.name for variant in variants], ["ctx-100tokens", "ctx-1k"])
            for variant in variants:
                manifest = json.loads(
                    (variant / "context-manifest.json").read_text(encoding="utf-8")
                )
                self.assertGreaterEqual(manifest["actual_tokens"], manifest["target_tokens"])
                self.assertEqual(manifest["relevant_files"], ["src/relevant.py"])
                self.assertFalse(list(Draft202012Validator(schema).iter_errors(manifest)))
                self.assertTrue((variant / "generated-distractors").is_dir())

    def test_seed_controls_generated_context_and_tokenizer_fallback_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            source.mkdir()
            (source / "file.txt").write_text("base context\n", encoding="utf-8")
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            generate_context_variants(source, first, [200], seed=1)
            generate_context_variants(source, second, [200], seed=2)
            first_path = next((first / "ctx-200tokens" / "generated-distractors").glob("*.md"))
            second_path = next((second / "ctx-200tokens" / "generated-distractors").glob("*.md"))
            first_text = first_path.read_text(encoding="utf-8")
            second_text = second_path.read_text(encoding="utf-8")
            self.assertNotEqual(first_text, second_text)
        self.assertGreater(count_tokens("one, two!").tokens, 0)

    def test_relevant_file_metrics_keep_unnecessary_edits_visible(self) -> None:
        result = score_relevant_files(["src/billing.py"], ["src/billing.py", "README.md"])
        self.assertEqual(result["relevant_file_precision"], 0.5)
        self.assertEqual(result["relevant_file_recall"], 1.0)
        self.assertEqual(result["unnecessary_files_modified"], ["README.md"])

    def test_missing_relevant_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            source.mkdir()
            (source / "file.txt").write_text("context\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                generate_context_variants(
                    source, Path(directory) / "variants", [100], relevant_files=["src/missing.py"]
                )


if __name__ == "__main__":
    unittest.main()
