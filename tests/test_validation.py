from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runner.validation import run_validator


class ValidationTests(unittest.TestCase):
    def test_runs_argument_list_without_shell(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_validator(
                {"command": ["python", "-c", "print('ok')"]}, Path(directory), 10
            )

            self.assertTrue(result.passed)
            self.assertEqual(result.stdout.strip(), "ok")

    def test_enforces_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_validator(
                {"command": ["python", "-c", "import time; time.sleep(5)"], "timeout_seconds": 1},
                Path(directory),
                10,
            )

            self.assertTrue(result.timed_out)
            self.assertFalse(result.passed)


if __name__ == "__main__":
    unittest.main()
