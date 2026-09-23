"""Generate controlled long-context variants from one task workspace."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from runner.context_dataset import generate_context_variants  # noqa: E402


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--sizes",
        default="10000,30000,60000,100000,150000,200000",
        help="comma-separated target token counts",
    )
    parser.add_argument("--relevant-file", action="append", default=[])
    parser.add_argument("--tokenizer", help="optional tiktoken encoding name")
    parser.add_argument("--seed", type=int, default=20260915)
    options = parser.parse_args(arguments)
    try:
        sizes = [int(value.strip()) for value in options.sizes.split(",") if value.strip()]
    except ValueError as exc:
        parser.error(f"invalid --sizes: {exc}")
    variants = generate_context_variants(
        options.source,
        options.output,
        sizes,
        relevant_files=options.relevant_file,
        tokenizer_name=options.tokenizer,
        seed=options.seed,
    )
    summary = [
        json.loads(
            (variant.parent / f"{variant.name}.context-manifest.json").read_text(encoding="utf-8")
        )
        for variant in variants
    ]
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
