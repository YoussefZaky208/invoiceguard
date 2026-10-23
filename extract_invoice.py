import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# The "form" we want Gemini to fill in
class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    amount: float


class Invoice(BaseModel):
    supplier: str
    invoice_number: str
    invoice_date: str
    line_items: list[LineItem]
    subtotal: float
    tax: float
    total: float


with open("invoice1.png", "rb") as f:
    image_bytes = f.read()

response = client.models.generate_content(
    model=os.getenv("GEMINI_MODEL"),
    contents=[
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
        "Extract the data from this invoice.",
    ],
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=Invoice,
    ),
)

invoice = response.parsed  # Gemini's answer, already turned into our Invoice form

print("Supplier:", invoice.supplier)
print("Number:  ", invoice.invoice_number)
print("Items:   ", len(invoice.line_items))
print("Total:   ", invoice.total)



# ---------- Step 9: validation checks ----------
problems = []

# Check 1: important fields are not empty
if not invoice.supplier or not invoice.invoice_number:
    problems.append("Missing supplier or invoice number")

# Check 2: each line's quantity x price = amount
for item in invoice.line_items:
    expected = item.quantity * item.unit_price
    if abs(expected - item.amount) > 0.05:
        problems.append(f"Line '{item.description}': {item.quantity} x {item.unit_price} should be {expected}, but invoice says {item.amount}")

# Check 3: the items add up to the subtotal
items_sum = sum(item.amount for item in invoice.line_items)
if abs(items_sum - invoice.subtotal) > 0.05:
    problems.append(f"Items add up to {items_sum}, but subtotal says {invoice.subtotal}")

# Check 4: subtotal + tax = total
if abs(invoice.subtotal + invoice.tax - invoice.total) > 0.05:
    problems.append(f"Subtotal + tax = {invoice.subtotal + invoice.tax}, but total says {invoice.total}")

print()
if problems:
    print("PROBLEMS FOUND:")
    for p in problems:
        print(" -", p)
else:
    print("All checks passed. Invoice looks correct.")




# ---------- Step 11: save to database ----------
import sqlite3

db = sqlite3.connect("invoices.db")
db.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        supplier TEXT,
        invoice_number TEXT,
        invoice_date TEXT,
        total REAL,
        status TEXT
    )
""")

existing = db.execute(
    "SELECT COUNT(*) FROM invoices WHERE supplier = ? AND invoice_number = ?",
    (invoice.supplier, invoice.invoice_number),
).fetchone()[0]

print()
if existing > 0:
    print("DUPLICATE: this invoice is already in the database. Not saved again.")
else:
    status = "needs_review" if problems else "approved"
    db.execute(
        "INSERT INTO invoices VALUES (?, ?, ?, ?, ?)",
        (invoice.supplier, invoice.invoice_number, invoice.invoice_date, invoice.total, status),
    )
    db.commit()
    print(f"Saved to database with status: {status}")

print("\nEverything in the database:")
for row in db.execute("SELECT * FROM invoices"):
    print(" ", row)
db.close()
