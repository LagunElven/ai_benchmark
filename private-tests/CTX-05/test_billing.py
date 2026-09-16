from decimal import Decimal

from src.billing import calculate_total

assert calculate_total([Decimal("19.99"), Decimal("0.01")], Decimal("25"), Decimal("8.5")) == Decimal("16.28")
assert calculate_total([Decimal("100.00"), Decimal("50.00")], Decimal("10"), Decimal("20")) == Decimal("162.00")
assert calculate_total([Decimal("48.25")], Decimal("12.5"), None) == Decimal("42.22")
assert calculate_total([Decimal("5.00")], None, Decimal("5")) == Decimal("5.25")
print("hidden CTX-05 checks passed")
