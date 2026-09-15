from pathlib import Path

from extract import extract_rows

rows = extract_rows((Path(__file__).parents[1] / "document.txt").read_text(encoding="utf-8"))
assert rows == [
    {"sku": "A-100", "quantity": 2, "unit_price": 12.5, "line_total": 25.0},
    {"sku": "B-200", "quantity": 1, "unit_price": 7.25, "line_total": 7.25},
]
print("public table checks passed")
