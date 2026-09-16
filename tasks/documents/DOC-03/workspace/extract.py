def extract_payment_summary(text):
    values = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip().lower()] = value.strip()
    amount_value = values.get("amount due", "0 EUR")
    amount = float(amount_value.split()[0].replace(",", "."))
    return {
        "reference": values.get("reference", ""),
        "due_date": values.get("due date", ""),
        "amount": amount,
        "currency": amount_value.split()[-1],
    }
