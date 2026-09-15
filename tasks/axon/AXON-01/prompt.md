# Basic event handler

Implement the event handlers in `StockProjection`. `StockAdded` increases the SKU
quantity and `StockRemoved` decreases it, but a removal that would make stock negative
must be ignored. Ignore null events, blank SKUs and non-positive quantities. Unknown
event types are ignored. `available` returns zero for an unknown SKU. Keep the records
and method signatures and do not modify tests.
