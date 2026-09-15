# JPA N+1 order summaries

Implement `OrderSummaryService.load`. Fetch orders once and customers in one batch
through `Repository.findCustomersByIds`; do not perform one customer query per order.
Preserve order order, render unknown customers as `"<unknown>"`, and return an empty
list for a null repository. The repository query counter is part of the contract: a
load should use at most two queries. Keep the records and API unchanged.
