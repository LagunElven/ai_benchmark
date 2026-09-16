# DOC-01 — digital purchase order

Implement `extract_purchase_order(text)` in `extract.py` for the supplied
digital-document text rendering. Return exactly `order_number`, `issue_date`,
`supplier`, `currency`, and `total_net`.

Field labels and their spacing around `:` are case-insensitive. Normalize the
date to ISO `YYYY-MM-DD`, the currency to uppercase, and accept either a dot or
comma decimal separator for `total_net`. Ignore headings and unknown fields.
Raise `ValueError` when a required field is missing or the date, currency,
identifier, or amount is malformed. Return `total_net` as a JSON-compatible
number and do not mutate the input text.

This is a digital/PDF text-rendering task; it does not require a PDF or OCR
library. Do not modify the document or tests. Return only a `file_changes_v1`
JSON object.
