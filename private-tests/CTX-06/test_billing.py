from decimal import Decimal

from src.billing import calculate_total

assert calculate_total([Decimal("100.00"), Decimal("50.00")], Decimal("10"), Decimal("20")) == Decimal("162.00")
assert calculate_total([Decimal("19.99"), Decimal("0.01")], Decimal("25"), Decimal("8.5")) == Decimal("16.28")
assert calculate_total([Decimal("250.00")], Decimal("12"), Decimal("19.6")) == Decimal("263.12")
assert calculate_total([Decimal("0.005")], None, None) == Decimal("0.01")
print("hidden CTX-06 checks passed")
