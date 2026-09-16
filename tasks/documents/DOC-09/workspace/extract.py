def extract_documents(text):
    documents = []
    for block in text.split("---"):
        values = {}
        for line in block.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            values[key.strip().lower()] = value.strip()
        document_type = values.get("document type", "").upper()
        if document_type != "INVOICE":
            continue
        documents.append({
            "type": "INVOICE",
            "document_id": values.get("invoice number", ""),
            "date": values.get("date", ""),
            "amount": float(values.get("total", "0")),
            "currency": values.get("currency", ""),
        })
    return documents
