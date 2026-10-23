"""Automated tests for InvoiceGuard's business rules and database.

Run with:  pytest
These tests never call the AI, so they are instant and use no API quota.
"""

import core
import pytest


def make_invoice(**changes) -> core.Invoice:
    """A correct invoice; pass keyword arguments to break it in specific ways."""
    data = {
        "supplier": "Nile Office Supplies Co.",
        "invoice_number": "INV-2026-0147",
        "invoice_date": "2026-10-05",
        "currency": "EGP",
        "line_items": [
            core.LineItem(description="A4 Paper", quantity=10, unit_price=250, amount=2500),
            core.LineItem(description="Ink Cartridge", quantity=4, unit_price=620, amount=2480),
        ],
        "subtotal": 4980,
        "tax": 697.20,
        "total": 5677.20,
    }
    data.update(changes)
    return core.Invoice(**data)


@pytest.fixture(autouse=True)
def temporary_database(tmp_path, monkeypatch):
    """Give every test its own empty database so tests never affect each other."""
    monkeypatch.setattr(core, "DB_PATH", str(tmp_path / "test.db"))


# ---------- business rules ----------
def test_correct_invoice_has_no_problems():
    assert core.validate_invoice(make_invoice()) == []


def test_overcharged_line_is_caught():
    lines = [
        core.LineItem(description="A4 Paper", quantity=10, unit_price=250, amount=3500),  # should be 2,500
        core.LineItem(description="Ink Cartridge", quantity=4, unit_price=620, amount=2480),
    ]
    problems = core.validate_invoice(make_invoice(line_items=lines, subtotal=5980, tax=837.20, total=6817.20))
    assert len(problems) == 1
    assert "A4 Paper" in problems[0]


def test_subtotal_not_matching_items_is_caught():
    problems = core.validate_invoice(make_invoice(subtotal=6980, tax=977.20, total=7957.20))
    assert any("Items add up to" in p for p in problems)


def test_inflated_total_is_caught():
    problems = core.validate_invoice(make_invoice(total=6427.20))
    assert any("Subtotal + tax" in p for p in problems)


def test_missing_invoice_number_is_caught():
    assert "Missing invoice number" in core.validate_invoice(make_invoice(invoice_number=""))


def test_small_rounding_differences_are_allowed():
    assert core.validate_invoice(make_invoice(total=5677.24)) == []


# ---------- database and duplicates ----------
def test_clean_invoice_is_approved_and_flagged_one_needs_review():
    _, status = core.save_invoice(make_invoice(), [])
    assert status == "approved"
    _, status = core.save_invoice(make_invoice(invoice_number="INV-2026-0148"), ["some problem"])
    assert status == "needs_review"


def test_duplicate_is_blocked_even_with_different_formatting():
    first_id, _ = core.save_invoice(make_invoice(), [])
    same_invoice = make_invoice(supplier="NILE OFFICE SUPPLIES CO", invoice_number="inv 2026 0147")
    duplicate_id, status = core.save_invoice(same_invoice, [])
    assert status == "duplicate"
    assert duplicate_id == first_id
    assert len(core.list_invoices()) == 1


def test_human_review_changes_status():
    invoice_id, _ = core.save_invoice(make_invoice(), ["some problem"])
    assert core.set_status(invoice_id, "rejected") is True
    assert core.get_invoice(invoice_id)["status"] == "rejected"
    assert core.total_by_status("rejected") == 5677.20


def test_review_rejects_unknown_ids_and_decisions():
    assert core.set_status(999, "approved") is False
    with pytest.raises(ValueError):
        core.set_status(1, "maybe")
