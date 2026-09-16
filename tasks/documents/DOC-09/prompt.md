# DOC-09 — mixed document types

Implement `extract_documents(text)` in `extract.py` for a transcript containing
multiple documents separated by `---`. Support `INVOICE` and `RECEIPT` blocks
and return a list in source order. Each result must contain exactly `type`,
`document_id`, `date`, `amount`, and `currency`.

Invoices use `INVOICE NUMBER` and `TOTAL`; receipts use `RECEIPT NUMBER` and
`AMOUNT PAID`. Field labels are case-insensitive. Normalize dates from
`YYYY-MM-DD` or `DD/MM/YYYY` to ISO, parse dot/comma decimal amounts, and
uppercase currencies. Ignore unsupported document types and unrelated lines,
but raise `ValueError` for a supported block with a missing or malformed
required field. Do not modify the document or tests. Return only a
`file_changes_v1` JSON object.
