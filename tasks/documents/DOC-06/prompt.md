# Invoice table extraction

Implement `extract_rows(text)` for the OCR post-processing layer. The input contains a
pipe-delimited table with a header `SKU | QTY | UNIT_PRICE`, optional separator/blank
lines, and rows such as `A-100 | 2 | 12.50`. Return a list of objects with exactly the
keys `sku` (trimmed string), `quantity` (integer), `unit_price` (number), and
`line_total` (quantity multiplied by unit price, rounded to two decimals). Accept a
comma decimal separator, ignore lines that do not contain three columns, and never
include the header as data. Preserve row order and raise `ValueError` for a data row
with a non-numeric quantity or price. Do not modify tests. Return a `file_changes_v1`
response.
