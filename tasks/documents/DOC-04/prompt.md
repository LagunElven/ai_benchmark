# DOC-04 — rotated delivery document

Implement `extract_delivery_note(text)` in `extract.py` for the OCR transcript
of a document whose source page was rotated. Return exactly `reference`,
`warehouse`, `delivery_date`, and `packages`.

The transcript contains an orientation marker that must be ignored. Fields may
appear in any order. Normalize `delivery_date` from `DD/MM/YYYY` or
`YYYY-MM-DD` to ISO `YYYY-MM-DD`, trim the warehouse and reference, and parse
the package count as an integer. Raise `ValueError` for a missing or malformed
required field. The validator is orientation-independent because it consumes
the deterministic OCR text transcript rather than a native image decoder.

Do not modify the document or tests. Return only a `file_changes_v1` JSON
object.
