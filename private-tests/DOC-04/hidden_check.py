from extract import extract_delivery_note


assert extract_delivery_note(
    """ORIENTATION: 270
TOTAL PACKAGES: 04
DELIVERY DATE: 2026-07-18
REFERENCE: DN-270-2
WAREHOUSE: BORDEAUX-01
Noise: ignored
"""
) == {
    "reference": "DN-270-2",
    "warehouse": "BORDEAUX-01",
    "delivery_date": "2026-07-18",
    "packages": 4,
}


def assert_invalid(value):
    try:
        extract_delivery_note(value)
    except ValueError:
        return
    raise AssertionError("malformed rotated document was accepted")


assert_invalid("REFERENCE: DN-1\nWAREHOUSE: A\nDELIVERY DATE: 31/02/2026\nTOTAL PACKAGES: 1")
assert_invalid("REFERENCE: DN-1\nWAREHOUSE: A\nDELIVERY DATE: 01/02/2026")
print("hidden rotated document checks passed")
