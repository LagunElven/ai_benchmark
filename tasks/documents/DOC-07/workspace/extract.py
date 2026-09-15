def extract_form(text):
    values = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()
    return {
        "claim_id": values.get("claim id", ""),
        "amount": float(values.get("amount", "0")),
        "currency": values.get("currency", ""),
        "date": values.get("date", ""),
    }
