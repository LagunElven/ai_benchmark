import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from extract import extract_noisy_totals

result = extract_noisy_totals(
    (Path(__file__).parents[1] / "noisy-invoice.txt").read_text(encoding="utf-8")
)
assert result == {
    "invoice_number": "INV-NOISY-11",
    "currency": "EUR",
    "tax": 20.50,
    "total": 1234.50,
}
print("public noisy invoice checks passed")
