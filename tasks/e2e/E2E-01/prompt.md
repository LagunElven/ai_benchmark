# REST DTO to UI card

The dependency-free harness models a Spring REST response consumed by an Angular
component. `api.get_order` returns the stable wire DTO with `id`, `totalCents` and
`currency`. Fix `ui.to_order_card` so it consumes that DTO and returns exactly
`{"id": ..., "amount": "12.50 EUR"}` for a 1,250-cent order.

Reject a missing/invalid DTO with `ValueError`, require a non-empty string id and
currency, and format cents with two decimal places without floating-point drift. Keep
the API module unchanged and do not modify tests. Return a `file_changes_v1` response.
