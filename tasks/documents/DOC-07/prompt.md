# Claim form extraction

Implement `extract_form(text)` for OCR text containing one `KEY: VALUE` field per line.
Return exactly `claim_id` (trimmed string), `amount` (number with comma or dot decimal),
`currency` (uppercase three-letter code), and `date` (ISO `YYYY-MM-DD`). Keys and field
names are case-insensitive; ignore unknown fields and blank lines. Raise `ValueError`
when a required field is missing or the amount/date/currency is malformed. Do not
modify tests. Return a `file_changes_v1` response.
