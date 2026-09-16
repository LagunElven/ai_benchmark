def extract_delivery_note(text):
    values = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()
    return {
        "reference": values.get("reference", ""),
        "warehouse": values.get("warehouse", ""),
        "delivery_date": values.get("delivery date", ""),
        "packages": int(values.get("total packages", "0")),
    }
