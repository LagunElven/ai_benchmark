def extract_multipage_invoice(text):
    lines = text.splitlines()
    result = {
        "invoice_number": "",
        "invoice_date": "",
        "currency": "",
        "line_items": [],
        "total": 0,
    }
    for line in lines:
        if line.startswith("INVOICE:"):
            result["invoice_number"] = line.split(":", 1)[1].strip()
        elif line.startswith("DATE:"):
            result["invoice_date"] = line.split(":", 1)[1].strip()
        elif line.startswith("CURRENCY:"):
            result["currency"] = line.split(":", 1)[1].strip()
        elif line.startswith("TOTAL:"):
            result["total"] = float(line.split(":", 1)[1])
        elif "|" in line and not line.startswith("DESCRIPTION"):
            columns = [column.strip() for column in line.split("|")]
            if len(columns) == 4:
                result["line_items"].append({
                    "description": columns[0],
                    "quantity": int(columns[1]),
                    "unit_price": float(columns[2]),
                    "amount": float(columns[3]),
                })
    return result
