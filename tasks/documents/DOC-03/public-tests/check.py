import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from extract import extract_payment_summary

result = extract_payment_summary((Path(__file__).parents[1] / "scan-150dpi.txt").read_text(encoding="utf-8"))
assert result == {
    "reference": "INV-150-009",
    "due_date": "2026-06-30",
    "amount": 2049.90,
    "currency": "EUR",
}
print("public 150 DPI checks passed")
