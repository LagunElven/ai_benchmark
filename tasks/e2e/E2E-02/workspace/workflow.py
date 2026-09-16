from angular_client import build_reserve_command
from axon_aggregate import handle_reserve
from jpa_projection import apply_stock_reserved


def reserve_stock(
    product_id: str,
    quantity: int,
    expected_version: int,
    aggregate: dict[str, object],
    read_model: dict[str, object],
) -> dict[str, object]:
    command = build_reserve_command(product_id, quantity, expected_version)
    event = handle_reserve(command, aggregate)
    return apply_stock_reserved(read_model, event)
