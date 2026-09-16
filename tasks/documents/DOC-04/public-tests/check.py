import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from extract import extract_delivery_note

result = extract_delivery_note(
    (Path(__file__).parents[1] / "rotated-document.txt").read_text(encoding="utf-8")
)
assert result == {
    "reference": "DN-90-007",
    "warehouse": "LYON-03",
    "delivery_date": "2026-07-18",
    "packages": 4,
}
print("public rotated document checks passed")
