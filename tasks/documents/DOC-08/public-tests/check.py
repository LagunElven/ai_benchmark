import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from extract import extract_multipage_invoice

result = extract_multipage_invoice(
    (Path(__file__).parents[1] / "document.txt").read_text(encoding="utf-8")
)
assert result == {
    "invoice_number": "INV-MP-2026-01",
    "invoice_date": "2026-08-01",
    "currency": "EUR",
    "line_items": [
        {"description": "Platform support", "quantity": 2, "unit_price": 100.0, "amount": 200.0},
        {"description": "Security audit", "quantity": 1, "unit_price": 250.5, "amount": 250.5},
    ],
    "total": 450.5,
}
print("public multi-page checks passed")
