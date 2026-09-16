import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from src.billing import calculate_total

actual = calculate_total([Decimal("100.00"), Decimal("50.00")], Decimal("10"), Decimal("20"))
assert actual == Decimal("162.00"), actual
assert calculate_total([Decimal("0.005")], None, None) == Decimal("0.01")
print("public long-context checks passed")
