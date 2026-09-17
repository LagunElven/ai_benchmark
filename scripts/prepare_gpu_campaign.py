"""Freeze local inputs and check readiness for one remote GPU campaign."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from runner.gpu_preflight import build_preflight_manifest, write_preflight_manifest  # noqa: E402


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign-id", required=True, help="planned id, for example C-003")
    parser.add_argument("--config", type=Path, default=REPOSITORY_ROOT / "benchmark.yaml")
    parser.add_argument(
        "--serving-config", type=Path, default=REPOSITORY_ROOT / "serving" / "config.yaml"
    )
    parser.add_argument(
        "--plan", type=Path, default=REPOSITORY_ROOT / "campaigns" / "gpu" / "plan.yaml"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="manifest destination (default: results/raw/preflight/<campaign-id>-preflight.json)",
    )
    parser.add_argument(
        "--require-clean",
        action="store_true",
        help="fail when the repository has uncommitted or untracked files",
    )
    parser.add_argument(
        "--allow-pending",
        action="store_true",
        help="return success while exact model/engine values are still pending",
    )
    options = parser.parse_args(arguments)
    config_path = (
        options.config if options.config.is_absolute() else REPOSITORY_ROOT / options.config
    )
    output = options.output or (
        config_path.parent
        / "results"
        / "raw"
        / "preflight"
        / f"{options.campaign_id}-preflight.json"
    )
    try:
        manifest = build_preflight_manifest(
            config_path=config_path,
            serving_config_path=options.serving_config,
            plan_path=options.plan,
            campaign_id=options.campaign_id,
            require_clean=options.require_clean,
        )
    except Exception as exc:  # CLI boundary: provide a concise actionable error.
        print(f"preflight error: {exc}", file=sys.stderr)
        return 2
    path = write_preflight_manifest(manifest, output)
    print(json.dumps({"status": manifest["status"], "manifest": str(path)}, ensure_ascii=False))
    if manifest["status"] == "ready":
        return 0
    if manifest["status"] == "pending" and options.allow_pending:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
