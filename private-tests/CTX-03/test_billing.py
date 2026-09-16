from decimal import Decimal

from src.billing import calculate_total

assert calculate_total([Decimal("80.00"), Decimal("20.00")], Decimal("15"), Decimal("7.5")) == Decimal("91.38")
assert calculate_total([Decimal("12.34")], None, None) == Decimal("12.34")
assert calculate_total([Decimal("75.00")], Decimal("100"), Decimal("20")) == Decimal("0.00")
assert calculate_total([Decimal("0.01"), Decimal("0.02")], Decimal("50"), Decimal("10")) == Decimal("0.02")
print("hidden CTX-03 checks passed")
