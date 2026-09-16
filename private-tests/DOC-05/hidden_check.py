from extract import extract_noisy_totals


assert extract_noisy_totals(
    """INVOICE NO : INV-2
CURRENCY: CHF
TOTAL :: 1.234,56
TAX\t:\t0,10
"""
) == {
    "invoice_number": "INV-2",
    "currency": "CHF",
    "tax": 0.10,
    "total": 1234.56,
}


def assert_invalid(value):
    try:
        extract_noisy_totals(value)
    except ValueError:
        return
    raise AssertionError("malformed noisy invoice was accepted")


assert_invalid("INVOICE NO: INV-1\nCURRENCY: EUR\nTAX: 1.00")
assert_invalid("INVOICE NO: INV-1\nCURRENCY: EURO\nTAX: 1.00\nTOTAL: 2.00")
assert_invalid("INVOICE NO: INV-1\nCURRENCY: EUR\nTAX: bad\nTOTAL: 2.00")
print("hidden noisy invoice checks passed")
