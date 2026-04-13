import base64
import json
import tempfile
import os
from pdf2image import convert_from_path
from openai import OpenAI

# 🔐 USE ENV VARIABLE (DO THIS)
client = OpenAI(api_key=os.getenv("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"))


# 📄 Convert PDF → Images
def pdf_to_images(pdf_path):
    images = convert_from_path(
        pdf_path,
        poppler_path="poppler/Library/bin"  # ✅ IMPORTANT for EXE
    )

    image_paths = []

    for i, image in enumerate(images):
        path = f"page_{i}.png"
        image.save(path, "PNG")
        image_paths.append(path)

    return image_paths


# 🧠 Encode image to base64
def encode_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")


# 🤖 Extract structured data
def extract_from_image(image_path):
    base64_image = encode_image(image_path)

    prompt = """You are an expert invoice data extractor.

Carefully read the invoice image and extract data EXACTLY as shown.

Definitions:
- Vendor = the company that ISSUED the invoice (seller)
- Customer = the company receiving the invoice (buyer)

Rules:
- Always extract Vendor (seller), NOT customer
- Vendor is usually at the top with GST, address, logo
- Ignore "Bill To" and "Ship To"
- Do NOT guess values
- Do NOT cut text
- Extract FULL product name exactly as written
- Quantity must be a number only
- Price must be unit price (not total)
- If unsure, leave field empty

Return ONLY valid JSON in this format:
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

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=800,
            temperature=0,
            timeout=60  # ✅ prevents timeout crash
        )

        raw_output = response.choices[0].message.content

        # Clean markdown if present
        cleaned = raw_output.replace("```json", "").replace("```", "").strip()

        return json.loads(cleaned)

    except Exception as e:
        print("❌ Extraction error:", e)
        return None


# 🚀 MAIN FUNCTION
def process_invoice(pdf_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        pdf_path = tmp.name

    images = pdf_to_images(pdf_path)

    results = []

    # ✅ Only first page (faster + avoids timeout)
    for img in images[:1]:
        result = extract_from_image(img)
        if result:
            results.append(result)

    return results