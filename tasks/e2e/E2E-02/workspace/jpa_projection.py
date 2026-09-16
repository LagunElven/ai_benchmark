def apply_stock_reserved(
    read_model: dict[str, object], event: dict[str, object]
) -> dict[str, object]:
    if event.get("type") != "StockReserved":
        raise ValueError("unsupported event")
    if event.get("aggregateId") != read_model.get("productId"):
        raise ValueError("aggregate mismatch")
    quantity = event.get("quantity")
    remaining = event.get("remaining")
    version = event.get("version")
    current_version = read_model.get("version")
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("invalid reservation quantity")
    if type(remaining) is not int or remaining < 0:
        raise ValueError("invalid remaining quantity")
    if type(current_version) is not int or type(version) is not int:
        raise ValueError("invalid projection version")
    if version != current_version + 1:
        raise ValueError("event version is not contiguous")
    projected = dict(read_model)
    projected["available"] = remaining
    projected["reserved"] = quantity
    projected["version"] = version
    return projected
