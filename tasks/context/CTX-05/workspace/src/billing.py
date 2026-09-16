from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def calculate_total(lines: list[Decimal], discount_percent: Decimal | None,
                    tax_percent: Decimal | None) -> Decimal:
    """Calculate an invoice total; this implementation contains a subtle bug."""
    subtotal = sum(lines, Decimal("0.00"))
    discount = discount_percent or Decimal("0")
    tax = tax_percent or Decimal("0")
    discounted = subtotal + (subtotal * discount / Decimal("100"))
    return (discounted + (discounted * tax / Decimal("100"))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
