# DOC-03 — 150 DPI OCR scan

Implement `extract_payment_summary(text)` in `extract.py` using the supplied
`fixtures/ocr-notes.md`. Return exactly `reference`, `due_date`, `amount`, and
`currency`.

The 150 DPI transcript may contain spaces between thousands, a comma decimal,
and the OCR confusion `O` for `0` only inside the numeric amount. Normalize the
date to ISO `YYYY-MM-DD`, convert the amount to a number rounded to two decimal
places, and uppercase the currency. Do not replace letters in the reference or
other text globally. Raise `ValueError` for missing fields, malformed dates,
amounts, or currencies.

The OCR note is a deterministic fixture contract, not a claim that every OCR
engine makes the same substitutions. Do not modify the document, note, or
tests. Return only a `file_changes_v1` JSON object.
