import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from extract import extract_documents

result = extract_documents(
    (Path(__file__).parents[1] / "mixed-documents.txt").read_text(encoding="utf-8")
)
assert result == [
    {
        "type": "INVOICE",
        "document_id": "INV-MIX-01",
        "date": "2026-08-10",
        "amount": 120.0,
        "currency": "EUR",
    },
    {
        "type": "RECEIPT",
        "document_id": "RCP-MIX-02",
        "date": "2026-08-11",
        "amount": 15.5,
        "currency": "EUR",
    },
]
print("public mixed document checks passed")
