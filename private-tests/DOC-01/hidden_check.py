from extract import extract_purchase_order


assert extract_purchase_order(
    """PURCHASE ORDER
ORDER NUMBER: PO-9
ISSUE DATE: 12/04/2026
SUPPLIER: Atelier du Sud
CURRENCY: eur
TOTAL NET: 12,50
Notes: ignored
"""
) == {
    "order_number": "PO-9",
    "issue_date": "2026-04-12",
    "supplier": "Atelier du Sud",
    "currency": "EUR",
    "total_net": 12.5,
}


def assert_invalid(value):
    try:
        extract_purchase_order(value)
    except ValueError:
        return
    raise AssertionError("malformed purchase order was accepted")


assert_invalid("ORDER NUMBER: PO-1\nISSUE DATE: 2026-01-01\nSUPPLIER: A\nCURRENCY: EUR")
assert_invalid("ORDER NUMBER: PO-1\nISSUE DATE: 2026-99-01\nSUPPLIER: A\nCURRENCY: EUR\nTOTAL NET: 1.00")
print("hidden digital document checks passed")
