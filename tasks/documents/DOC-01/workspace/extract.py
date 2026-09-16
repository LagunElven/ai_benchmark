def extract_purchase_order(text):
    values = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()
    return {
        "order_number": values.get("order number", ""),
        "issue_date": values.get("issue date", ""),
        "supplier": values.get("supplier", ""),
        "currency": values.get("currency", ""),
        "total_net": float(values.get("total net", "0")),
    }
