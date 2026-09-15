# Multi-revision event upcaster

Upgrade an `OrderCreated` payload without losing data. Revisions are strings:

- revision `0` has `totalCents` and must become revision `1` with `amountCents`;
- revision `1` must become revision `2` by adding `currency: EUR` only when absent;
- revision `2` is already current and must pass through unchanged.

Apply every required step in one call, preserve unknown properties, do not mutate the
input map, and reject unknown revisions. Return a new immutable result with the final
revision. Keep the public API and do not modify tests.
