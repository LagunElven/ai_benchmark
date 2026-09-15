# Multi-aggregate command routing

Implement `AggregateRouter.dispatch`. A command targets exactly one supported aggregate
(`Order` or `Customer`) by its type and id; increment that aggregate's counter by the
command amount and return its new value. Commands with null/blank type or id,
non-positive amounts, or unknown types must be rejected with `IllegalArgumentException`.
State for one aggregate must never leak into another. Keep the public API and do not
modify tests.
