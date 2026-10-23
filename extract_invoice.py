"""Process one invoice from the command line.

Usage:  python extract_invoice.py invoice1.png
"""

import sys

import core

if len(sys.argv) != 2:
    print("Usage: python extract_invoice.py <invoice file>")
    sys.exit(1)

path = sys.argv[1]
mime_type = "application/pdf" if path.lower().endswith(".pdf") else (
    "image/jpeg" if path.lower().endswith((".jpg", ".jpeg")) else "image/png"
)

with open(path, "rb") as f:
    result = core.process_invoice(f.read(), mime_type)

invoice = result["invoice"]
print(f"Supplier: {invoice['supplier']}")
print(f"Number:   {invoice['invoice_number']}")
print(f"Items:    {len(invoice['line_items'])}")
print(f"Total:    {invoice['total']:,.2f} {invoice['currency']}")
print()
if result["problems"]:
    print("PROBLEMS FOUND:")
    for problem in result["problems"]:
        print(" -", problem)
else:
    print("All checks passed.")
print(f"\nStatus: {result['status']} (id {result['id']})")
