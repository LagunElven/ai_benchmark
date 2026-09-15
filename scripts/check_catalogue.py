"""Check the quality-task catalogue against discovered task definitions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from runner.catalogue import catalogue_coverage  # noqa: E402


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue", type=Path, default=REPOSITORY_ROOT / "catalogue.yaml")
    parser.add_argument("--require-complete", action="store_true")
    options = parser.parse_args(arguments)
    summary = catalogue_coverage(REPOSITORY_ROOT, options.catalogue)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    if (
        summary["missing_implemented"]
        or summary["category_mismatches"]
        or summary["missing_validation"]
        or summary["unexpected_tasks"]
    ):
        return 1
    if options.require_complete and summary["implemented_tasks"] != summary["target_tasks"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
