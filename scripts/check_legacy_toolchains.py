"""Report optional native legacy compilers available on this machine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from runner.legacy import detect_toolchains  # noqa: E402


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", dest="as_json")
    options = parser.parse_args(arguments)
    detected = detect_toolchains()
    if options.as_json:
        print(json.dumps(detected, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for name, details in detected.items():
            status = details["path"] or "not found"
            print(f"{name}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
