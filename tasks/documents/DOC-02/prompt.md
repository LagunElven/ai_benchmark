# DOC-02 — 300 DPI claim scan

Implement `extract_claim(text)` in `extract.py` for the OCR transcript of the
supplied 300 DPI scan. Return exactly `reference`, `beneficiary`,
`service_date`, `amount`, `currency`, and `status`.

Field labels are case-insensitive and may have arbitrary spaces around `:`.
Normalize the service date from `YYYY/MM/DD` or `DD/MM/YYYY` to ISO
`YYYY-MM-DD`; accept dot, comma, or spaces as decimal/thousands separators;
uppercase the three-letter currency and status. Preserve the beneficiary and
reference text after trimming. Ignore unknown fields. Raise `ValueError` for
missing required fields, invalid dates, invalid currencies, or malformed
amounts.

The scan and OCR transcript are deterministic fixtures; no OCR engine is
required. Do not modify the document or tests. Return only a `file_changes_v1`
JSON object.
