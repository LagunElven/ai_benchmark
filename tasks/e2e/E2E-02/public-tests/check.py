import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from angular_client import build_reserve_command
from axon_aggregate import handle_reserve
from jpa_projection import apply_stock_reserved
from workflow import reserve_stock


command = build_reserve_command("sku-1", 3, 0)
assert command == {
    "type": "ReserveStock",
    "payload": {"productId": "sku-1", "quantity": 3, "expectedVersion": 0},
}
aggregate = {"productId": "sku-1", "available": 10, "version": 0}
event = handle_reserve(command, aggregate)
assert event == {
    "type": "StockReserved",
    "aggregateId": "sku-1",
    "quantity": 3,
    "remaining": 7,
    "version": 1,
}
assert apply_stock_reserved(
    {"productId": "sku-1", "available": 10, "reserved": 0, "version": 0}, event
) == {"productId": "sku-1", "available": 7, "reserved": 3, "version": 1}
assert reserve_stock(
    "sku-1", 3, 0, aggregate, {"productId": "sku-1", "available": 10, "reserved": 0, "version": 0}
) == {"productId": "sku-1", "available": 7, "reserved": 3, "version": 1}
print("public e2e-02 checks passed")
