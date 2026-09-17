"""Run or display the reproducible serving benchmark matrix."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from serving.benchmark import ServingBenchmark, load_serving_config  # noqa: E402


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=REPOSITORY_ROOT / "serving" / "config.yaml"
    )
    parser.add_argument(
        "--output-dir", type=Path, default=REPOSITORY_ROOT / "results" / "raw" / "serving"
    )
    parser.add_argument(
        "--plan-only", action="store_true", help="Print cases without contacting the endpoint"
    )
    options = parser.parse_args(arguments)
    config = load_serving_config(options.config)
    benchmark = ServingBenchmark(config, options.output_dir)
    if options.plan_only:
        print(json.dumps(benchmark.plan(), ensure_ascii=False, indent=2))
        return 0
    result = benchmark.run(progress=lambda message: print(message, flush=True))
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
