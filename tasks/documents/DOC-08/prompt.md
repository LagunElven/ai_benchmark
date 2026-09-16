# DOC-08 — multi-page invoice

Implement `extract_multipage_invoice(text)` in `extract.py`. The OCR text
contains page markers and a repeated table header. Return exactly
`invoice_number`, `invoice_date`, `currency`, `line_items`, and `total`.

Combine line items from every page in reading order and ignore page markers,
blank lines, and repeated `DESCRIPTION | QTY | UNIT PRICE | AMOUNT` headers.
Each line item must contain the trimmed `description`, integer `quantity`, and
numeric `unit_price` and `amount`. Accept dot or comma decimals, normalize the
date to ISO `YYYY-MM-DD`, and round monetary values to two decimals. Raise
`ValueError` for missing document fields or malformed table rows. Do not stop
after the first page and do not modify the document or tests. Return only a
`file_changes_v1` JSON object.
