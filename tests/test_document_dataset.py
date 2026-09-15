from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from runner.document_dataset import generate_dataset, load_document_spec


class DocumentDatasetTests(unittest.TestCase):
    def test_generator_writes_all_variants_and_manifest(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = root / "datasets" / "documents" / "invoice-001.json"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "invoice"
            manifest_path = generate_dataset(source, output, seed=7)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["document_id"], "invoice-001")
            self.assertEqual(
                {variant["name"] for variant in manifest["variants"]},
                {
                    "digital-300dpi",
                    "digital-150dpi",
                    "rotated-300dpi",
                    "noisy-150dpi",
                    "compressed-150dpi",
                },
            )
            for variant in manifest["variants"]:
                path = output / variant["path"]
                self.assertTrue(path.is_file())
                self.assertGreater(path.stat().st_size, 32)
            transforms = {variant["name"]: variant["transform"] for variant in manifest["variants"]}
            self.assertEqual(transforms["rotated-300dpi"]["degrees"], 90)
            self.assertEqual(transforms["noisy-150dpi"]["seed"], 7)
            self.assertEqual(transforms["compressed-150dpi"]["levels"], 4)
            self.assertTrue((output / "ground-truth.json").is_file())

    def test_same_seed_produces_byte_identical_dataset(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = root / "datasets" / "documents" / "invoice-001.json"
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            generate_dataset(source, first, seed=11)
            generate_dataset(source, second, seed=11)
            first_files = sorted(
                path.relative_to(first) for path in first.rglob("*") if path.is_file()
            )
            second_files = sorted(
                path.relative_to(second) for path in second.rglob("*") if path.is_file()
            )
            self.assertEqual(first_files, second_files)
            for relative in first_files:
                self.assertEqual((first / relative).read_bytes(), (second / relative).read_bytes())

    def test_generator_rejects_non_empty_output_and_invalid_source(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = root / "datasets" / "documents" / "invoice-001.json"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output"
            output.mkdir()
            (output / "keep.txt").write_text("do not overwrite", encoding="utf-8")
            with self.assertRaises(ValueError):
                generate_dataset(source, output)
            invalid = Path(directory) / "invalid.json"
            invalid.write_text(json.dumps({"id": "bad"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_document_spec(invalid)


if __name__ == "__main__":
    unittest.main()
