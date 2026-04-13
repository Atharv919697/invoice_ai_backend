import base64
import json
from openai import OpenAI

client = OpenAI()


def extract_from_pdf(pdf_bytes):
    # ✅ Convert PDF → base64
    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    # ✅ FIX: Add correct data URL prefix
    data_url = f"data:application/pdf;base64,{base64_pdf}"

    prompt = """You are an expert invoice data extractor.

Extract data from this invoice PDF.

Rules:
- Vendor = seller (NOT customer)
- Ignore "Bill To"
- Extract FULL product name
- Quantity = number only
- Price = unit price

Return ONLY JSON:

{
  "date": "",
  "vendor": "",
  "items": [
    {
      "name": "",
      "quantity": "",
      "price": ""
    }
  ],
  "total": ""
}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "file",
                        "file": {
                            "filename": "invoice.pdf",
                            "file_data": data_url  # ✅ FIXED
                        }
                    }
                ]
            }
        ],
        temperature=0
    )

    output = response.choices[0].message.content

    # ✅ Clean markdown safely
    cleaned = output.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except Exception as e:
        print("⚠️ JSON parsing failed")
        print(cleaned)
        return {"error": "Invalid JSON", "raw": cleaned}


def process_invoice(pdf_bytes):
    result = extract_from_pdf(pdf_bytes)
    return [result]
