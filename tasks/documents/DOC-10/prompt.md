# DOC-10 — structured invoice extraction

Implement `extract.py` so it reads the supplied `document.txt` and writes one
UTF-8 JSON object to the output path. Extract exactly the invoice number, ISO
date, currency, subtotal, tax, total and every line item with description,
quantity, unit price and amount. Amounts must be JSON numbers rounded to two
decimal places; do not invent fields or values. The output must be deterministic
and use only the Python standard library. Do not modify the document or tests.
Return only the `file_changes_v1` JSON object.

The input is a digital text rendering of a document; OCR-specific quality is
tracked separately when image tooling is available.
