from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class LegacyNativeTests(unittest.TestCase):
    def test_cobol_native_runner_skips_cleanly_without_cobc(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = (
            root
            / "tasks"
            / "legacy"
            / "cobol"
            / "COBOL-05"
            / "workspace"
            / "legacy"
            / "order-total.cbl"
        )
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(root / "scripts" / "run_cobol_native.py"),
                    str(source),
                    "--output-dir",
                    directory,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
        result = json.loads(completed.stdout)
        if result["status"] == "skipped":
            self.assertEqual(result["reason"], "cobc not found")
        else:
            self.assertIn(result["status"], {"compiled", "passed"})


if __name__ == "__main__":
    unittest.main()
