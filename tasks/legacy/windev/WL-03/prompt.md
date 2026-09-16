# WL-03 — WLanguage order charge

Read the synthetic pseudo source and its supplied `fixtures/wlanguage-reference.md`
before correcting `OrderCharge.totalWithShipping`.

For a non-negative subtotal, normalize the delivery mode by trimming it and
comparing case-insensitively. `PICKUP` adds 0.00, `EXPRESS` adds 12.50, and
`STANDARD` adds 0.00 when the subtotal is at least 50.00, otherwise 6.90.
Unknown or null modes and negative subtotals must raise
`IllegalArgumentException`. Return the total rounded to two decimals with
`BigDecimal`; never use binary floating point.

The WLanguage source and reference are explicitly synthetic and do not claim
proprietary compiler semantics. Preserve the Java API, do not modify supplied
fixtures or tests, and return only the `file_changes_v1` JSON object.
