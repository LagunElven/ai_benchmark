from extract import extract_claim


assert extract_claim(
    """SCAN 300 DPI
Claim Reference: CLM-2
Beneficiary: Bob Martin
Date of Service: 09/05/2026
Amount TTC: 2.345,70 eur
Status: pending
"""
) == {
    "reference": "CLM-2",
    "beneficiary": "Bob Martin",
    "service_date": "2026-05-09",
    "amount": 2345.70,
    "currency": "EUR",
    "status": "PENDING",
}


def assert_invalid(value):
    try:
        extract_claim(value)
    except ValueError:
        return
    raise AssertionError("malformed claim scan was accepted")


assert_invalid("CLAIM REFERENCE: C\nBENEFICIARY: A\nDATE OF SERVICE: 2026/02/30\nAMOUNT TTC: 1.00 EUR\nSTATUS: OK")
assert_invalid("CLAIM REFERENCE: C\nBENEFICIARY: A\nDATE OF SERVICE: 2026/02/01\nSTATUS: OK")
print("hidden 300 DPI checks passed")
