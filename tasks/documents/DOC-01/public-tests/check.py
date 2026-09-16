import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from extract import extract_purchase_order

result = extract_purchase_order((Path(__file__).parents[1] / "document.txt").read_text(encoding="utf-8"))
assert result == {
    "order_number": "PO-2026-0017",
    "issue_date": "2026-03-12",
    "supplier": "Northwind Services",
    "currency": "EUR",
    "total_net": 2400.0,
}
print("public digital document checks passed")
