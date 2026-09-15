# WL-04 — WLanguage migration with supplied reference

The supplied legacy/late-fee.wlanguage.pseudo is explicitly synthetic
pseudocode, not a claim about proprietary WinDev syntax. Use its accompanying
fixture documentation to implement src/main/java/LateFee.java.

The rule is: no fee for zero or negative late days; five percent of the amount
for 1–30 late days; ten percent for more than 30 days. Round the final result
to two decimals with BigDecimal and never use binary floating point. Preserve
the Java method signature and modify no tests or reference files. Return only
the file_changes_v1 JSON object.
