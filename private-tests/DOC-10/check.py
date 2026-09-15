from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

document = Path(sys.argv[1])
extractor = Path(sys.argv[2])
with tempfile.TemporaryDirectory() as directory:
    output = Path(directory) / "result.json"
    subprocess.run([sys.executable, str(extractor), str(document), str(output)], check=True)
    actual = json.loads(output.read_text(encoding="utf-8"))
expected = {
    "currency": "EUR",
    "invoice_date": "2026-02-14",
    "invoice_number": "INV-2026-0042",
    "line_items": [
        {
            "amount": 200.00,
            "description": "Monthly platform support",
            "quantity": 2,
            "unit_price": 100.00,
        },
        {
            "amount": 1034.50,
            "description": "Security review",
            "quantity": 1,
            "unit_price": 1034.50,
        },
    ],
    "subtotal": 1234.50,
    "tax": 246.90,
    "total": 1481.40,
}
assert actual == expected, (actual, expected)
print("hidden document extraction checks passed")
