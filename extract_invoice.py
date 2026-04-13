import base64
import json
from openai import OpenAI

client = OpenAI()


def extract_from_pdf(pdf_bytes):
    base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

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
                            "file_data": base64_pdf
                        }
                    }
                ]
            }
        ],
        temperature=0
    )

    output = response.choices[0].message.content
    cleaned = output.replace("```json", "").replace("```", "").strip()

    return json.loads(cleaned)


def process_invoice(pdf_bytes):
    result = extract_from_pdf(pdf_bytes)
    return [result]
