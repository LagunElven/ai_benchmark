def get_order(order_id: str, total_cents: int, currency: str) -> dict[str, object]:
    return {"id": order_id, "totalCents": total_cents, "currency": currency}
