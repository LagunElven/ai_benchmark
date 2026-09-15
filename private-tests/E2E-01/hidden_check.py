import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from api import get_order
from ui import to_order_card

assert get_order("o-2", 1, "CHF") == {"id": "o-2", "totalCents": 1, "currency": "CHF"}
assert to_order_card(get_order("o-2", 1, "CHF")) == {
    "id": "o-2",
    "amount": "0.01 CHF",
}
assert to_order_card(get_order("o-3", 999, "JPY"))["amount"] == "9.99 JPY"
for dto in ({}, {"id": "", "totalCents": 10, "currency": "EUR"},
            {"id": "o", "totalCents": -1, "currency": "EUR"}):
    try:
        to_order_card(dto)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid DTO was accepted")
print("hidden e2e checks passed")
