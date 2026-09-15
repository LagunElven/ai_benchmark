from decimal import Decimal

from src.billing import calculate_total

assert calculate_total(
    [Decimal("19.99"), Decimal("0.01")], Decimal("25"), Decimal("8.5")
) == Decimal("16.28")
assert calculate_total([Decimal("10.00")], Decimal("100"), None) == Decimal("0.00")
assert calculate_total([Decimal("10.00")], None, Decimal("5")) == Decimal("10.50")
print("hidden long-context checks passed")
