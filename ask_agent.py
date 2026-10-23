import os
import sqlite3
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=60000),
)

# ---------- The agent's tools ----------
def list_invoices() -> list[dict]:
    """Returns every invoice in the database with its supplier, invoice number, date, total, and status."""
    print("   [agent used tool: list_invoices]")
    db = sqlite3.connect("invoices.db")
    rows = db.execute("SELECT supplier, invoice_number, invoice_date, total, status FROM invoices").fetchall()
    db.close()
    return [
        {"supplier": r[0], "invoice_number": r[1], "date": r[2], "total": r[3], "status": r[4]}
        for r in rows
    ]


def total_by_status(status: str) -> float:
    """Returns the total amount in EGP of all invoices with the given status: 'approved' or 'needs_review'."""
    print(f"   [agent used tool: total_by_status('{status}')]")
    db = sqlite3.connect("invoices.db")
    result = db.execute("SELECT SUM(total) FROM invoices WHERE status = ?", (status,)).fetchone()[0]
    db.close()
    return result or 0.0


# ---------- The agent ----------
chat = client.chats.create(
    model=os.getenv("GEMINI_MODEL"),
    config=types.GenerateContentConfig(
        tools=[list_invoices, total_by_status],
        system_instruction=(
            "You are an assistant for a company's accounts team. "
            "Answer questions about invoices using your tools. "
            "Never guess numbers; always get them from a tool. "
            "If a question is not about invoices, politely say you can only help with invoices."
        ),
    ),
)

print("InvoiceGuard agent ready. Type 'quit' to stop.")
while True:
    question = input("\nYou: ")
    if question.lower() == "quit":
        break
    try:
        response = chat.send_message(question)
        print("Agent:", response.text)
    except Exception as error:
        print("Agent: Sorry, Gemini is busy or unreachable right now. Please ask again in a moment.")
        print("   [details:", str(error)[:80], "]")