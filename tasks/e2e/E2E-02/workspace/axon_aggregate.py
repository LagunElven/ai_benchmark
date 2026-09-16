def handle_reserve(command: dict[str, object], aggregate: dict[str, object]) -> dict[str, object]:
    if command.get("type") != "ReserveStock":
        raise ValueError("unsupported command")
    payload = command.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("command payload is required")
    product_id = payload.get("productId")
    quantity = payload.get("quantity")
    expected_version = payload.get("expectedVersion")
    if product_id != aggregate.get("productId"):
        raise ValueError("aggregate mismatch")
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("quantity must be positive")
    if expected_version != aggregate.get("version"):
        raise ValueError("stale aggregate version")
    available = aggregate.get("available")
    if type(available) is not int or available < quantity:
        raise ValueError("insufficient stock")
    version = aggregate.get("version")
    if type(version) is not int or version < 0:
        raise ValueError("invalid aggregate version")
    return {
        "type": "StockReserved",
        "aggregateId": product_id,
        "quantity": quantity,
        "remaining": available - quantity,
        "version": version + 1,
    }
