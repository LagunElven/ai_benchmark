"""Perform the short endpoint smoke required before a paid campaign."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from serving.client import OpenAICompatibleServingClient  # noqa: E402


def _get_models(base_url: str, api_key_env: str | None, timeout: float) -> list[str]:
    headers = {}
    if api_key_env and os.environ.get(api_key_env):
        headers["Authorization"] = f"Bearer {os.environ[api_key_env]}"
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/models", headers=headers, method="GET"
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload: dict[str, Any] = json.loads(response.read().decode("utf-8"))
    return [
        str(item["id"])
        for item in payload.get("data", [])
        if isinstance(item, dict) and "id" in item
    ]


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key-env", default=None)
    parser.add_argument("--timeout", type=float, default=60)
    options = parser.parse_args(arguments)
    result: dict[str, Any] = {
        "base_url": options.base_url,
        "model": options.model,
        "status": "failed",
    }
    try:
        models = _get_models(options.base_url, options.api_key_env, options.timeout)
        result["models"] = models
        if models and options.model not in models:
            raise RuntimeError(f"model id not advertised by /models: {options.model}")
        measurement = OpenAICompatibleServingClient(
            options.base_url,
            options.model,
            timeout_seconds=options.timeout,
            api_key_env=options.api_key_env,
        ).complete_stream(
            [{"role": "user", "content": "Reply with exactly: READY"}],
            max_output_tokens=8,
            temperature=0.0,
            top_p=1.0,
            seed=42,
            request_id="endpoint-smoke",
        )
        result["measurement"] = measurement.as_dict("endpoint-smoke", measurement.started)
        result["status"] = "ready" if measurement.status == "completed" else "failed"
    except (
        OSError,
        urllib.error.URLError,
        urllib.error.HTTPError,
        json.JSONDecodeError,
        RuntimeError,
    ) as exc:
        result["error"] = str(exc)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
