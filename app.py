from fastapi import FastAPI, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import openpyxl
from extract_invoice import process_invoice

app = FastAPI()

# ✅ Enable CORS (for HTML page)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EXCEL_FILE = "invoices.xlsx"


# 📄 Create Excel if not exists
def create_excel_if_not_exists():
    if not os.path.exists(EXCEL_FILE):
        wb = openpyxl.Workbook()
        ws = wb.active

        # Header
        ws.append(["date", "vendor", "name", "quantity", "price", "total"])

        wb.save(EXCEL_FILE)


# ➕ Append data to Excel
def append_to_excel(data):
    wb = openpyxl.load_workbook(EXCEL_FILE)
    ws = wb.active

    for invoice in data:
        date = invoice.get("date", "")
        vendor = invoice.get("vendor", "")
        total = invoice.get("total", "")

        items = invoice.get("items", [])

        if not items:
            ws.append([date, vendor, "", "", "", total])
        else:
            for item in items:
                name = item.get("name", "")
                quantity = item.get("quantity", "")
                price = item.get("price", "")

                ws.append([
                    date,
                    vendor,
                    name,
                    quantity,
                    price,
                    total
                ])

    wb.save(EXCEL_FILE)


# 🚀 1. Extract invoice (ONLY returns data now)
@app.post("/extract-invoice")
async def extract_invoice(file: UploadFile = File(...)):

    try:
        # Save temp file
        file_location = f"temp_{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Read file bytes
        with open(file_location, "rb") as f:
            pdf_bytes = f.read()

        # Extract using AI
        results = process_invoice(pdf_bytes)

        # Delete temp file
        os.remove(file_location)

        return {
            "status": "success",
            "data": results
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# 💾 2. Save edited data to Excel
@app.post("/save-data")
async def save_data(data: list = Body(...)):

    try:
        create_excel_if_not_exists()
        append_to_excel(data)

        return {
            "status": "success",
            "message": "Data saved to Excel"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }