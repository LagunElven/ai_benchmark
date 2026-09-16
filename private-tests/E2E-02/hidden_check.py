from angular_client import build_reserve_command
from axon_aggregate import handle_reserve
from jpa_projection import apply_stock_reserved


initial_read_model = {
    "productId": "sku-2",
    "available": 10,
    "reserved": 0,
    "version": 0,
}
first_aggregate = {"productId": "sku-2", "available": 10, "version": 0}
first_event = handle_reserve(build_reserve_command("sku-2", 4, 0), first_aggregate)
after_first = apply_stock_reserved(initial_read_model, first_event)
second_aggregate = {"productId": "sku-2", "available": 6, "version": 1}
second_event = handle_reserve(build_reserve_command("sku-2", 2, 1), second_aggregate)
after_second = apply_stock_reserved(after_first, second_event)
assert after_second == {
    "productId": "sku-2",
    "available": 4,
    "reserved": 6,
    "version": 2,
}
assert initial_read_model == {
    "productId": "sku-2",
    "available": 10,
    "reserved": 0,
    "version": 0,
}


def expect_value_error(read_model, event):
    try:
        apply_stock_reserved(read_model, event)
    except ValueError:
        return
    raise AssertionError("invalid event was accepted")


expect_value_error(after_second, {**second_event, "version": 4})
expect_value_error(after_second, {**second_event, "version": 2})
expect_value_error(after_second, {**second_event, "type": "OtherEvent"})
expect_value_error(after_second, {**second_event, "quantity": 0})
expect_value_error(after_second, {**second_event, "remaining": -1})
expect_value_error({**after_second, "productId": "other"}, {**second_event, "version": 3})
print("hidden e2e-02 checks passed")
