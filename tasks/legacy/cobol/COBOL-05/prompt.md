# COBOL-05 — behavior-preserving migration

Read `legacy/order-total.cbl` and complete the Java migration in
`src/main/java/OrderTotal.java`. Preserve the COBOL behavior: add subtotal and
tax using two-decimal decimal arithmetic and cap the result at `9999999.99`.
Inputs are non-negative monetary values with at most two fractional digits;
return a `BigDecimal` scaled to two decimals. Do not use binary floating point,
do not change the public method signature, and do not modify tests or the COBOL
reference. Return only the `file_changes_v1` JSON object.

`cobc` is not required for this smoke harness; the source reference is included
so a migration model must use the supplied legacy documentation rather than
guessing a new business rule.
