from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runner.changes import apply_file_changes
from runner.errors import ChangeProtocolError


class ChangeProtocolTests(unittest.TestCase):
    def test_applies_utf8_file_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            changed = apply_file_changes(
                '{"changes":[{"path":"src/example.txt","content":"été\\n"}]}', workspace
            )

            self.assertEqual(changed, ["src/example.txt"])
            self.assertEqual(
                (workspace / "src" / "example.txt").read_text(encoding="utf-8"), "été\n"
            )

    def test_rejects_parent_traversal(self) -> None:
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaisesRegex(ChangeProtocolError, "Unsafe change path"),
        ):
            apply_file_changes(
                '{"changes":[{"path":"../secret.txt","content":"leak"}]}',
                Path(directory),
            )

    def test_rejects_extra_protocol_fields(self) -> None:
        with (
            tempfile.TemporaryDirectory() as directory,
            self.assertRaisesRegex(ChangeProtocolError, "only a 'changes' array"),
        ):
            apply_file_changes('{"changes":[],"explanation":"done"}', Path(directory))


if __name__ == "__main__":
    unittest.main()
