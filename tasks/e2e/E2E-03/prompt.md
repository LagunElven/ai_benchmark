# E2E-03 - legacy ledger rule to Java API

Read the supplied fixed-format COBOL rule in `legacy/ledger-adjust.cbl` and
complete the Java modernization in `src/main/java/LedgerService.java`. The
unchanged `LedgerApi.java` is the application-layer adapter that receives a wire
request and calls the service.

Preserve the legacy behavior: code `C` credits the balance, `D` debits it, `N`
leaves it unchanged, and any other code is invalid. `entries` must be applied in
order. Use exact `BigDecimal` arithmetic, reject null or negative amounts and
return values at scale two. An invalid code or malformed entry must result in
`IllegalArgumentException` at this dependency-free API boundary. Do not modify
the COBOL source, manifest, API adapter or tests. Return only the
`file_changes_v1` JSON object.
