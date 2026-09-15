"""Generate deterministic text, ground truth and raster document variants."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from runner.document_dataset import generate_dataset  # noqa: E402


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="JSON document source")
    parser.add_argument("output", type=Path, help="empty output directory")
    parser.add_argument("--seed", type=int, default=20260915)
    options = parser.parse_args(arguments)
    manifest = generate_dataset(options.source, options.output, seed=options.seed)
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
