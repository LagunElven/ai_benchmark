# WL-01 — WLanguage shipment status

Read `legacy/shipment-status.wlanguage.pseudo` and complete the Java
compatibility target `ShipmentStatus.classify`.

The supplied file is synthetic WLanguage pseudocode, not a claim about
proprietary syntax. Reject negative quantities or a shipped quantity greater
than the ordered quantity with `IllegalArgumentException`. Compute the
remaining quantity. If it is zero, return `COMPLETE`; otherwise return
`OVERDUE` when `daysSincePromise` is greater than 2 and `OPEN` in all other
valid cases.

This scenario intentionally supplies no proprietary reference documentation:
infer only the stated business behavior from the pseudo source. Preserve the
enum and method signature, do not modify the source or tests, and return only
the `file_changes_v1` JSON object.
