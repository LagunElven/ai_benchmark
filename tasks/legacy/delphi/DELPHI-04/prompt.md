# DELPHI-04 — Delphi to Java migration

Read the supplied legacy/CustomerBalance.pas fixture and implement the Java
equivalent in src/main/java/CustomerBalance.java. The legacy Currency function
subtracts the credit from the gross amount, clamps negative results to zero, and
returns two decimal places. Use BigDecimal, never binary floating point.
Preserve the public method signature and do not modify the legacy source or
tests. Return only the file_changes_v1 JSON object.

The Pascal source is a small standard Object Pascal subset. The local machine
does not provide a Delphi compiler, so equivalence vectors are the executable
oracle and the fixture metadata records that limitation.
