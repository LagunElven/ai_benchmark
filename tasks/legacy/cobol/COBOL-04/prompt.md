# Behavior-preserving ledger modification

Read `legacy/ledger-adjust.cbl` and preserve the existing single-entry behavior in
`LedgerAdjuster.apply`. Code `C` credits the balance, `D` debits it, and `N` leaves it
unchanged; any other code is invalid. Amounts are non-negative decimal values with at
most two fractional digits, and every successful result must use scale two.

The maintenance request is to add `LedgerAdjuster.applyBatch`, which applies a list of
entries in order using exactly the same rules. Keep the existing `Entry` record and
`apply` signature. A null or empty batch returns the normalized starting balance; null
inputs, null entries, negative amounts, or values with more than two fractional digits
must raise `IllegalArgumentException`. Use `BigDecimal` only, do not mutate the entry
list or source reference, and do not regress the original operation behavior.
