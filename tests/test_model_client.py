from __future__ import annotations

import io
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from runner.client import OpenAICompatibleClient
from runner.config import load_benchmark_config
from runner.errors import ContextCapacityError
from tests.support import create_repository


class ModelClientTests(unittest.TestCase):
    def test_context_window_http_error_is_classified_as_capacity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = load_benchmark_config(create_repository(Path(directory)))
            config.data["model"]["base_url"] = "http://127.0.0.1:9999/v1"
            client = OpenAICompatibleClient(config)
            error = urllib.error.HTTPError(
                "http://127.0.0.1:9999/v1/chat/completions",
                400,
                "Bad Request",
                {},
                io.BytesIO(b"maximum context length exceeded"),
            )
            with (
                patch("runner.client.urllib.request.urlopen", side_effect=error),
                self.assertRaisesRegex(ContextCapacityError, "maximum context length"),
            ):
                client.complete(
                    [{"role": "user", "content": "large prompt"}], max_output_tokens=10
                )


if __name__ == "__main__":
    unittest.main()
