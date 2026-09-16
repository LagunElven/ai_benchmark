# DOC-05 — noisy compressed invoice

Implement `extract_noisy_totals(text)` in `extract.py` for the supplied OCR
transcript. Return exactly `invoice_number`, `currency`, `tax`, and `total`.

The transcript may contain repeated punctuation after labels, tabs, non-breaking
spaces, and locale-formatted numbers. Recognize `INVOICE NO`, `CURRENCY`,
`TAX`, and `TOTAL` labels case-insensitively; ignore unrelated noise. Remove
thousands separators safely, accept comma or dot decimal separators, uppercase
the currency, and return numeric values rounded to two decimals. Raise
`ValueError` when a required field or a valid amount/currency is absent.

This is a deterministic OCR post-processing fixture, not a claim about a
particular compression codec or OCR engine. Do not modify the document or
tests. Return only a `file_changes_v1` JSON object.
