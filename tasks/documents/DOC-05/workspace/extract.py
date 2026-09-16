def extract_noisy_totals(text):
    values = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()
    return {
        "invoice_number": values.get("invoice no", ""),
        "currency": values.get("currency", ""),
        "tax": float(values.get("tax", "0")),
        "total": float(values.get("total", "0")),
    }
