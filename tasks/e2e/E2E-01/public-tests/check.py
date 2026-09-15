import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from api import get_order
from ui import to_order_card

assert to_order_card(get_order("o-1", 1250, "EUR")) == {
    "id": "o-1",
    "amount": "12.50 EUR",
}
print("public e2e checks passed")
