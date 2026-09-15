"""Score OCR text and/or structured JSON extraction against ground truth."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from runner.document_metrics import score_fields, score_text  # noqa: E402


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected", type=Path, required=True, help="ground-truth JSON")
    parser.add_argument("--actual", type=Path, help="candidate JSON output")
    parser.add_argument("--reference-text", type=Path, help="canonical text")
    parser.add_argument("--hypothesis-text", type=Path, help="OCR text")
    parser.add_argument("--schema", type=Path, help="optional JSON schema for actual output")
    options = parser.parse_args(arguments)
    if options.actual is None and options.hypothesis_text is None:
        parser.error("provide --actual and/or --hypothesis-text")

    expected = json.loads(options.expected.read_text(encoding="utf-8"))
    report: dict[str, object] = {}
    if options.actual is not None:
        candidate_text = options.actual.read_text(encoding="utf-8")
        try:
            candidate = json.loads(candidate_text) if candidate_text.strip() else None
        except json.JSONDecodeError:
            candidate = None
        schema = (
            json.loads(options.schema.read_text(encoding="utf-8"))
            if options.schema is not None
            else None
        )
        report["structured"] = score_fields(
            expected, candidate if isinstance(candidate, dict) else None, schema=schema
        )
    if options.reference_text is not None and options.hypothesis_text is not None:
        report["text"] = score_text(
            options.reference_text.read_text(encoding="utf-8"),
            options.hypothesis_text.read_text(encoding="utf-8"),
        )
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
