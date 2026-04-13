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

Your task is to extract invoice data from the PDF.

VERY IMPORTANT DEFINITIONS:

- Vendor = the company that ISSUED the invoice (seller)
- Customer = the company receiving the invoice (buyer)

STRICT RULES:

- ALWAYS extract the Vendor (seller), NOT the customer
- Vendor is usually:
  • At the TOP of the invoice
  • Has GST number, address, logo
  • Appears as "From", "Seller", or company header

- IGNORE:
  • "Bill To"
  • "Ship To"
  • Customer details

- NEVER return customer as vendor

DATA RULES:

- Extract FULL product name exactly
- Quantity = number only
- Price = unit price (not total)
- Do NOT guess values

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
