def to_order_card(dto):
    return {
        "id": dto["id"],
        "amount": f"{dto['total_cents'] / 100:.2f} {dto['currency']}",
    }
