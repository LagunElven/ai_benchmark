# ABAL-01 — ABAL tax-band rule

Read `legacy/tax-band.abal.pseudo` and complete the Java compatibility target
`TaxBand.classify`.

The file is synthetic ABAL pseudocode, not a claim about a proprietary ABAL
grammar. ABAL means Advanced Business Application Language, not SAP ABAP. For
a non-null, non-negative annual income, return `NON_RESIDENT` when the person
is not resident. For residents, return `BASIC` at or below 1,000,000 cents,
`STANDARD` above that and at or below 3,000,000 cents, and `HIGH` above
3,000,000 cents. Reject null or negative income with
`IllegalArgumentException`.

This is the no-documentation comprehension variant: no proprietary reference
document is supplied. Preserve the enum and method signature, do not modify
the pseudo source or tests, and return only the `file_changes_v1` JSON object.
