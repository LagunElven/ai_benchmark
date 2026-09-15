def extract_rows(text):
    rows = []
    for line in text.splitlines():
        columns = line.split("|")
        if len(columns) != 3:
            continue
        if columns[0].strip().upper() == "SKU":
            continue
        rows.append({
            "sku": columns[0],
            "quantity": int(columns[1]),
            "unit_price": float(columns[2]),
            "line_total": 0,
        })
    return rows
