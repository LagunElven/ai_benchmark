from __future__ import annotations

import json
import sys


def extract(input_path: str, output_path: str) -> None:
    with open(input_path, encoding="utf-8") as stream:
        lines = stream.read().splitlines()
    result = {"invoice_number": "", "invoice_date": "", "currency": "", "subtotal": 0,
              "tax": 0, "total": 0, "line_items": []}
    for line in lines:
        if line.startswith("INVOICE:"):
            result["invoice_number"] = line.split(":", 1)[1].strip()
        elif line.startswith("DATE:"):
            result["invoice_date"] = line.split(":", 1)[1].strip()
        elif line.startswith("CURRENCY:"):
            result["currency"] = line.split(":", 1)[1].strip()
        elif line.startswith("SUBTOTAL:"):
            result["subtotal"] = float(line.split(":", 1)[1])
        elif line.startswith("TAX:"):
            result["tax"] = float(line.split(":", 1)[1])
        elif line.startswith("TOTAL:"):
            result["total"] = float(line.split(":", 1)[1])
    with open(output_path, "w", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, sort_keys=True)


if __name__ == "__main__":
    extract(sys.argv[1], sys.argv[2])
