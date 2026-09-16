# Sequential file and COMP-3 migration

Read `legacy/daily-sales.cbl` and complete the portable Java target
`PostedSales.totalPosted`. The COBOL program reads sequential records and adds the
signed packed-decimal `SALE-AMOUNT` only when the one-character status is exactly `P`.
The supplied `fixtures/input-format.md` defines the textual representation used by the
Java harness; it is not a replacement COBOL syntax.

Return a `BigDecimal` scaled to two decimal places. A null or empty record list totals
`0.00`; preserve record order while processing, ignore non-posted statuses, accept
signed values with at most two fractional digits, and reject malformed records,
blank identifiers, blank amounts, or amounts with more than two fractional digits with
`IllegalArgumentException`. Do not use binary floating point, mutate the input list, or
modify the source reference or tests.
