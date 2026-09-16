def build_reserve_command(product_id: str, quantity: int, expected_version: int) -> dict[str, object]:
    if not isinstance(product_id, str) or not product_id.strip():
        raise ValueError("product id is required")
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("quantity must be a positive integer")
    if type(expected_version) is not int or expected_version < 0:
        raise ValueError("expected version must be non-negative")
    return {
        "type": "ReserveStock",
        "payload": {
            "productId": product_id,
            "quantity": quantity,
            "expectedVersion": expected_version,
        },
    }
