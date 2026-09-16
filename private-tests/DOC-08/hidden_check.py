from extract import extract_multipage_invoice


assert extract_multipage_invoice(
    """PAGE 1 OF 2
INVOICE: INV-2
DATE: 02/08/2026
CURRENCY: EUR
DESCRIPTION | QTY | UNIT PRICE | AMOUNT
First item | 1 | 10,00 | 10,00
PAGE 2 OF 2
DESCRIPTION | QTY | UNIT PRICE | AMOUNT
Second item | 3 | 2,50 | 7,50
TOTAL: 17,50
"""
) == {
    "invoice_number": "INV-2",
    "invoice_date": "2026-08-02",
    "currency": "EUR",
    "line_items": [
        {"description": "First item", "quantity": 1, "unit_price": 10.0, "amount": 10.0},
        {"description": "Second item", "quantity": 3, "unit_price": 2.5, "amount": 7.5},
    ],
    "total": 17.5,
}


def assert_invalid(value):
    try:
        extract_multipage_invoice(value)
    except ValueError:
        return
    raise AssertionError("malformed multi-page invoice was accepted")


assert_invalid("INVOICE: INV-1\nDATE: 2026-01-01\nCURRENCY: EUR\nTOTAL: 2.00")
assert_invalid("INVOICE: INV-1\nDATE: 2026-01-01\nCURRENCY: EUR\nDESCRIPTION | QTY | UNIT PRICE | AMOUNT\nA | x | 1.00 | 1.00\nTOTAL: 1.00")
print("hidden multi-page checks passed")
