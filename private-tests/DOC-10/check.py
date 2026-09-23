from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

expected = json.loads((Path(__file__).parent / "ground-truth.json").read_text(encoding="utf-8"))
document = Path(sys.argv[1])
extractor = Path(sys.argv[2])
with tempfile.TemporaryDirectory() as directory:
    output = Path(directory) / "result.json"
    subprocess.run([sys.executable, str(extractor), str(document), str(output)], check=True)
    actual = json.loads(output.read_text(encoding="utf-8"))
assert actual == expected, (actual, expected)
print("hidden document extraction checks passed")
