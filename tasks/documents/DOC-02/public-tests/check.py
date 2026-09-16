import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from extract import extract_claim

result = extract_claim((Path(__file__).parents[1] / "scan-300dpi.txt").read_text(encoding="utf-8"))
assert result == {
    "reference": "CLM-300-004",
    "beneficiary": "ALICE MARTIN",
    "service_date": "2026-05-09",
    "amount": 1250.50,
    "currency": "EUR",
    "status": "APPROVED",
}
print("public 300 DPI checks passed")
