# DELPHI-01 — Delphi stock fulfilment rule

Read `legacy/FulfillmentStatus.pas` and complete the Java compatibility target
`FulfillmentStatus.forStock`.

The Pascal function computes `Available := OnHand - Reserved`. Reject negative
values and a reserved quantity greater than stock with `IllegalArgumentException`.
When available stock is zero, return `BACKORDER`. Otherwise return `REORDER` when
available stock is less than or equal to the reorder point, and `READY` otherwise.
The comparison with the reorder point is inclusive.

Preserve the enum and method signature, do not modify the legacy source or tests,
and return only the `file_changes_v1` JSON object.
