# ABAL-03 — ABAL annual allowance migration

Read `legacy/annual-allowance.abal.pseudo` and implement its behavior in
`AnnualAllowance.payable`.

The supplied source is synthetic ABAL pseudocode, not a claim about proprietary
syntax. ABAL means Advanced Business Application Language, not SAP ABAP. Reject
null or negative `claimAmount` and `remainingCap` with
`IllegalArgumentException`. An unapproved claim pays `0.00`. For an approved
claim, pay the smaller of the claim amount and the remaining cap. Return a
`BigDecimal` rounded to two decimals with `RoundingMode.HALF_UP`; do not use
binary floating point.

This migration has no proprietary reference documentation beyond the pseudo
source and task contract. Preserve the public API, do not modify source or
tests, and return only the `file_changes_v1` JSON object.
