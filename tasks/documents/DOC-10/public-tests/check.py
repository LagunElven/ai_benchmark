from __future__ import annotations

import json
import sys
from pathlib import Path

value = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert value["invoice_number"] == "INV-2026-0042"
assert value["total"] == 1481.40
assert len(value["line_items"]) == 2
print("public document extraction checks passed")
