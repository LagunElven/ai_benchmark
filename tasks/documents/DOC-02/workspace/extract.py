def extract_claim(text):
    values = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()
    return {
        "reference": values.get("claim reference", ""),
        "beneficiary": values.get("beneficiary", ""),
        "service_date": values.get("date of service", ""),
        "amount": float(values.get("amount ttc", "0").split()[0].replace(",", ".")),
        "currency": values.get("amount ttc", "EUR").split()[-1],
        "status": values.get("status", ""),
    }
