from extract import extract_documents


assert extract_documents(
    """DOCUMENT TYPE: RECEIPT
RECEIPT NUMBER: R-1
DATE: 12/08/2026
AMOUNT PAID: 1.234,50 eur
CURRENCY: EUR
---
DOCUMENT TYPE: INVOICE
INVOICE NUMBER: I-2
DATE: 2026-08-13
TOTAL: 9,99
CURRENCY: chf
---
DOCUMENT TYPE: NOTE
NOTE ID: ignored
"""
) == [
    {
        "type": "RECEIPT",
        "document_id": "R-1",
        "date": "2026-08-12",
        "amount": 1234.5,
        "currency": "EUR",
    },
    {
        "type": "INVOICE",
        "document_id": "I-2",
        "date": "2026-08-13",
        "amount": 9.99,
        "currency": "CHF",
    },
]


def assert_invalid(value):
    try:
        extract_documents(value)
    except ValueError:
        return
    raise AssertionError("malformed supported document was accepted")


assert_invalid("DOCUMENT TYPE: RECEIPT\nRECEIPT NUMBER: R-1\nDATE: 2026-01-01\nCURRENCY: EUR")
assert_invalid("DOCUMENT TYPE: INVOICE\nINVOICE NUMBER: I-1\nDATE: 2026-01-01\nTOTAL: bad\nCURRENCY: EUR")
print("hidden mixed document checks passed")
