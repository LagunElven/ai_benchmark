from extract import extract_form

result = extract_form("CLAIM ID: C-2\nAMOUNT: 10,00\nCURRENCY: chf\nDATE: 2026-01-09\n")
assert result == {"claim_id": "C-2", "amount": 10.0, "currency": "CHF", "date": "2026-01-09"}
for text in (
    "CLAIM ID: C-2\nCURRENCY: EUR\nDATE: 2026-01-09\n",
    "CLAIM ID: C-2\nAMOUNT: nope\nCURRENCY: EUR\nDATE: 2026-01-09\n",
    "CLAIM ID: C-2\nAMOUNT: 10\nCURRENCY: EURO\nDATE: 2026-01-09\n",
    "CLAIM ID: C-2\nAMOUNT: 10\nCURRENCY: EUR\nDATE: 09/01/2026\n",
):
    try:
        extract_form(text)
    except ValueError:
        pass
    else:
        raise AssertionError("malformed form was accepted")
print("hidden form checks passed")
