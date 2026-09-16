# COBOL account-status comprehension

Read `legacy/account-status.cbl` and complete the Java compatibility target
`AccountStatus.classify`. The COBOL program gives zero balance precedence: a zero
balance is classified as `ZERO_BALANCE` regardless of overdue days. For a non-zero
balance, more than 30 overdue days is `DELINQUENT`; 30 days or fewer is `ACTIVE`.

Inputs are non-negative monetary values represented by `BigDecimal` and non-negative
day counts. Reject a null or negative balance and a negative day count with
`IllegalArgumentException`. Use exact decimal comparison, preserve the enum and method
signature, and do not modify the COBOL reference or tests.
