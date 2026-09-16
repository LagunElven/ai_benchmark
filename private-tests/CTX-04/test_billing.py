from decimal import Decimal

from src.billing import calculate_total

assert calculate_total([Decimal("100.00")], Decimal("10"), Decimal("20")) == Decimal("108.00")
assert calculate_total([Decimal("19.99"), Decimal("0.01")], Decimal("25"), Decimal("8.5")) == Decimal("16.28")
assert calculate_total([Decimal("100.005")], None, None) == Decimal("100.01")
assert calculate_total([Decimal("10.00")], None, Decimal("17.5")) == Decimal("11.75")
print("hidden CTX-04 checks passed")
