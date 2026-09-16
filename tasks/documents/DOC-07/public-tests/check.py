import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from extract import extract_form

result = extract_form((Path(__file__).parents[1] / "form.txt").read_text(encoding="utf-8"))
assert result == {
    "claim_id": "CLM-2026-001",
    "amount": 1250.50,
    "currency": "EUR",
    "date": "2026-04-07",
}
print("public form checks passed")
