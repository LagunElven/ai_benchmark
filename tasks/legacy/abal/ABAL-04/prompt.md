# ABAL-04 — documentation-assisted migration

ABAL means Advanced Business Application Language, not SAP ABAP. Read the
supplied legacy/benefit.abal.pseudo and fixtures/abal-reference.md before
editing src/main/java/BenefitRule.java. Both files are explicitly synthetic
pseudocode/reference material until a verified ABAL implementation is
available; do not invent proprietary syntax.

Implement the documented rule: members with at least twelve months of tenure
receive a five percent rebate from the base amount, otherwise the rebate is
zero. Round the final Java BigDecimal result to two decimals. Preserve the
public method signature, do not modify supplied documentation or tests, and
return only the file_changes_v1 JSON object.
