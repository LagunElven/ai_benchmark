from extract import extract_rows

rows = extract_rows(
    "SKU | QTY | UNIT_PRICE\n"
    " X-1 | 3 | 1,10 \n"
    "not a table\n"
    " X-2 | 2 | 0.335 \n"
    " X-3 | nope | 2.00\n"
)
assert rows[:2] == [
    {"sku": "X-1", "quantity": 3, "unit_price": 1.1, "line_total": 3.3},
    {"sku": "X-2", "quantity": 2, "unit_price": 0.34, "line_total": 0.68},
]
try:
    extract_rows("SKU | QTY | UNIT_PRICE\nX-3 | nope | 2.00\n")
except ValueError:
    pass
else:
    raise AssertionError("invalid numeric row was accepted")
print("hidden table checks passed")
