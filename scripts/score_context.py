"""Calculate relevant-file precision and recall for a context run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from runner.context_dataset import score_relevant_files  # noqa: E402


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--modified-file", action="append", required=True)
    options = parser.parse_args(arguments)
    manifest = json.loads(options.manifest.read_text(encoding="utf-8"))
    result = score_relevant_files(manifest["relevant_files"], options.modified_file)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
