"""InvoiceGuard REST API.

Run with:   uvicorn api:app --reload
Then open:  http://127.0.0.1:8000/docs
"""

from typing import Literal

from fastapi import FastAPI, File, HTTPException, UploadFile
from google.genai import errors
from pydantic import BaseModel

import core

app = FastAPI(
    title="InvoiceGuard API",
    description="Upload an invoice; the AI reads it, business rules check it, "
    "and flagged invoices wait for a human to approve or reject them.",
    version="0.1.0",
)

ALLOWED_TYPES = {"image/png", "image/jpeg", "application/pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@app.get("/health")
def health():
    """Quick check that the API is running."""
    return {"status": "ok"}


@app.post("/invoices", status_code=201)
def upload_invoice(file: UploadFile = File(...)):
    """Upload an invoice (PNG, JPEG or PDF). Returns the extracted data, any problems, and its status."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(415, f"Unsupported file type '{file.content_type}'. Use PNG, JPEG or PDF.")

    file_bytes = file.file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(413, "File is larger than 10 MB.")

    try:
        return core.process_invoice(file_bytes, file.content_type)
    except core.DailyQuotaExceeded as error:
        raise HTTPException(429, str(error))
    except errors.APIError as error:
        raise HTTPException(503, f"The AI service is unavailable right now, please retry. ({error.code})")


@app.get("/invoices")
def get_invoices(status: Literal["approved", "needs_review", "rejected"] | None = None):
    """List stored invoices, optionally filtered by status."""
    return core.list_invoices(status)


@app.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: int):
    """Get one invoice, including its line items."""
    invoice = core.get_invoice(invoice_id)
    if invoice is None:
        raise HTTPException(404, "Invoice not found.")
    return invoice


class Review(BaseModel):
    decision: Literal["approved", "rejected"]


@app.post("/invoices/{invoice_id}/review")
def review_invoice(invoice_id: int, review: Review):
    """Human-in-the-loop: a person approves or rejects an invoice."""
    if not core.set_status(invoice_id, review.decision):
        raise HTTPException(404, "Invoice not found.")
    return {"id": invoice_id, "status": review.decision}
