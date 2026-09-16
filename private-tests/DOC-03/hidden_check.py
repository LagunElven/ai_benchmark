from extract import extract_payment_summary


assert extract_payment_summary(
    """REFERENCE: INV-O-1
DUE DATE: 30/06/2026
AMOUNT DUE: 10O,105 eur
"""
) == {
    "reference": "INV-O-1",
    "due_date": "2026-06-30",
    "amount": 100.11,
    "currency": "EUR",
}


def assert_invalid(value):
    try:
        extract_payment_summary(value)
    except ValueError:
        return
    raise AssertionError("malformed 150 DPI transcript was accepted")


assert_invalid("REFERENCE: INV-1\nDUE DATE: 2026/02/30\nAMOUNT DUE: 1.00 EUR")
assert_invalid("REFERENCE: INV-1\nDUE DATE: 2026/02/01\nAMOUNT DUE: 1.2X EUR")
print("hidden 150 DPI checks passed")
