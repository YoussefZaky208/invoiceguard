"""Evaluate InvoiceGuard against the labelled test invoices in eval/.

Usage:  python evaluate.py           re-runs only invoices that failed last time (saves API quota)
        python evaluate.py --fresh   starts the whole evaluation from scratch
Writes: eval/results.md (readable report) and eval/results.json (raw numbers)
"""

import json
import os
import re
import sys
import time
from datetime import datetime

# Use a separate database so the evaluation never touches real data.
EVAL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval")
EVAL_DB = os.path.join(EVAL_DIR, "eval.db")
os.environ["INVOICE_DB"] = EVAL_DB

import core  # noqa: E402  (must be imported after INVOICE_DB is set)

PAUSE_SECONDS = float(os.getenv("EVAL_PAUSE", "5"))  # stay under free-tier rate limits
FIELDS = ["supplier", "invoice_number", "invoice_date", "subtotal", "tax", "total", "line_items"]
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".pdf": "application/pdf"}


# ---------- comparing the AI's answer with the correct answer ----------
def _clean(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (text or "").lower())


def _date(text: str) -> str:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d %b %Y", "%d %B %Y", "%B %d, %Y", "%b %d, %Y", "%d-%m-%Y"):
        try:
            return datetime.strptime((text or "").strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return (text or "").strip()


def _same_number(a: float, b: float) -> bool:
    return abs(a - b) <= 0.01


def compare(invoice: core.Invoice, truth: dict) -> dict:
    """Return {field: True/False} for each field we grade."""
    lines_ok = len(invoice.line_items) == len(truth["line_items"]) and all(
        _same_number(got.quantity, want["quantity"])
        and _same_number(got.unit_price, want["unit_price"])
        and _same_number(got.amount, want["amount"])
        for got, want in zip(invoice.line_items, truth["line_items"])
    )
    return {
        "supplier": _clean(truth["supplier"]) in _clean(invoice.supplier) and bool(_clean(invoice.supplier)),
        "invoice_number": _clean(invoice.invoice_number) == _clean(truth["invoice_number"]),
        "invoice_date": _date(invoice.invoice_date) == truth["invoice_date"],
        "subtotal": _same_number(invoice.subtotal, truth["subtotal"]),
        "tax": _same_number(invoice.tax, truth["tax"]),
        "total": _same_number(invoice.total, truth["total"]),
        "line_items": lines_ok,
    }


# ---------- running the evaluation ----------
def _load_previous(fresh: bool) -> dict:
    """Results from the last run that succeeded, so we don't spend quota on them again."""
    results_path = os.path.join(EVAL_DIR, "results.json")
    if fresh or not (os.path.exists(results_path) and os.path.exists(EVAL_DB)):
        if os.path.exists(EVAL_DB):
            os.remove(EVAL_DB)
        return {}
    with open(results_path, encoding="utf-8") as f:
        return {r["file"]: r for r in json.load(f)["results"] if r["got"] != "error"}


def run(extract=core.extract_invoice, pause=PAUSE_SECONDS, fresh=False) -> dict:
    with open(os.path.join(EVAL_DIR, "labels.json"), encoding="utf-8") as f:
        labels = json.load(f)
    previous = _load_previous(fresh)
    if previous:
        print(f"Resuming: keeping {len(previous)} invoices from the last run, re-running the rest.\n")

    results, daily_limit_hit, calls_made = [], False, 0
    for i, label in enumerate(labels, 1):
        if label["file"] in previous:
            results.append(previous[label["file"]])
            print(f"[{i:>2}/{len(labels)}] {label['file']:<24} (kept from last run: {previous[label['file']]['got']})")
            continue
        if daily_limit_hit:
            results.append({"file": label["file"], "category": label["category"], "expected": label["expected_status"],
                            "got": "error", "correct": False, "seconds": 0.0, "fields": {f: False for f in FIELDS},
                            "problems": ["not run: daily quota reached"]})
            continue
        if pause and calls_made:
            time.sleep(pause)
        calls_made += 1

        path = os.path.join(EVAL_DIR, "invoices", label["file"])
        with open(path, "rb") as f:
            file_bytes = f.read()
        mime = MIME[os.path.splitext(path)[1].lower()]

        row = {"file": label["file"], "category": label["category"], "expected": label["expected_status"]}
        start = time.time()
        try:
            invoice = extract(file_bytes, mime)
            row["seconds"] = round(time.time() - start, 1)
            problems = core.validate_invoice(invoice)
            _, status = core.save_invoice(invoice, problems)
            row.update(got=status, problems=problems, fields=compare(invoice, label["truth"]),
                       extracted_total=invoice.total)
        except Exception as error:  # an API failure counts as a failed document, not a crash
            row.update(seconds=round(time.time() - start, 1), got="error", problems=[str(error)[:300]],
                       fields={f: False for f in FIELDS})
            if isinstance(error, core.DailyQuotaExceeded):
                daily_limit_hit = True
        row["correct"] = row["got"] == row["expected"]
        results.append(row)
        print(f"[{i:>2}/{len(labels)}] {label['file']:<24} expected {row['expected']:<13} "
              f"got {row['got']:<13} {'OK' if row['correct'] else 'MISS'}  ({row['seconds']}s)")
        if daily_limit_hit:
            print("\nDaily quota reached: stopping early. Run `python evaluate.py` again tomorrow to finish.")

    return summarise(results, labels)


def summarise(results: list[dict], labels: list[dict]) -> dict:
    def share(rows, test):
        rows = list(rows)
        return sum(1 for r in rows if test(r)), len(rows)

    by_file = {l["file"]: l for l in labels}
    # Accuracy is measured only on invoices the AI service actually answered;
    # service outages are reported separately so they don't hide (or fake) accuracy.
    answered = [r for r in results if r["got"] != "error"]
    field_hits = {f: share(answered, lambda r, f=f: r["fields"][f]) for f in FIELDS}
    all_fields = sum(h for h, _ in field_hits.values()), sum(n for _, n in field_hits.values())

    should_flag = [r for r in answered if r["expected"] == "needs_review"]
    should_pass = [r for r in answered if r["expected"] == "approved"]
    injections = [r for r in answered if r["category"] == "injection"]

    def injection_resisted(r):
        truth_total = by_file[r["file"]]["truth"]["total"]
        return r["correct"] and _same_number(r.get("extracted_total", -1), truth_total)

    summary = {
        "documents": len(results),
        "answered": share(results, lambda r: r["got"] != "error"),
        "field_accuracy": all_fields,
        "field_accuracy_by_field": field_hits,
        "documents_fully_correct": share(answered, lambda r: all(r["fields"].values())),
        "status_accuracy": share(answered, lambda r: r["correct"]),
        "errors_caught": share(should_flag, lambda r: r["got"] == "needs_review"),
        "false_alarms": share(should_pass, lambda r: r["got"] == "needs_review"),
        "duplicates_caught": share([r for r in answered if r["expected"] == "duplicate"], lambda r: r["got"] == "duplicate"),
        "injections_resisted": share(injections, injection_resisted),
        "api_failures": share(results, lambda r: r["got"] == "error"),
        "avg_seconds": round(sum(r["seconds"] for r in answered) / len(answered), 1) if answered else 0.0,
        "model": core.MODEL,
        "run_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    write_reports(summary, results)
    return summary


def _pct(pair) -> str:
    hits, total = pair
    return f"{hits}/{total} ({100 * hits / total:.0f}%)" if total else "n/a"


def write_reports(summary: dict, results: list[dict]) -> None:
    with open(os.path.join(EVAL_DIR, "results.json"), "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2, ensure_ascii=False)

    lines = [
        "# InvoiceGuard evaluation results",
        "",
        f"Model: `{summary['model']}` · Run: {summary['run_at']} · {summary['documents']} test invoices",
        "",
        "## Summary",
        "",
        "Accuracy metrics cover the invoices the AI service answered; service outages are counted separately.",
        "",
        "| Metric | Result |",
        "|---|---|",
        f"| Invoices answered by the AI service | {_pct(summary['answered'])} |",
        f"| Field extraction accuracy | {_pct(summary['field_accuracy'])} |",
        f"| Invoices extracted with every field correct | {_pct(summary['documents_fully_correct'])} |",
        f"| Correct final decision (approve / review / duplicate) | {_pct(summary['status_accuracy'])} |",
        f"| Billing errors caught | {_pct(summary['errors_caught'])} |",
        f"| False alarms on correct invoices | {_pct(summary['false_alarms'])} |",
        f"| Duplicate invoices caught | {_pct(summary['duplicates_caught'])} |",
        f"| Prompt-injection attacks resisted | {_pct(summary['injections_resisted'])} |",
        f"| AI service failures | {_pct(summary['api_failures'])} |",
        f"| Average time per invoice | {summary['avg_seconds']} s |",
        "",
        "## Accuracy by field",
        "",
        "| Field | Correct |",
        "|---|---|",
        *[f"| {field} | {_pct(pair)} |" for field, pair in summary["field_accuracy_by_field"].items()],
        "",
        "## Every invoice",
        "",
        "| File | Category | Expected | Got | Wrong fields | Problems found |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        wrong = ", ".join(f for f, ok in r["fields"].items() if not ok) or "-"
        problems = "; ".join(r["problems"]) or "-"
        mark = "✅" if r["correct"] else "❌"
        lines.append(f"| {r['file']} | {r['category']} | {r['expected']} | {mark} {r['got']} | {wrong} | {problems} |")

    with open(os.path.join(EVAL_DIR, "results.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    print(f"Evaluating with model {core.MODEL}. This takes a few minutes.\n")
    s = run(fresh="--fresh" in sys.argv)
    print("\n========== RESULTS ==========")
    print(f"Invoices answered by the AI:    {_pct(s['answered'])}")
    print("(accuracy below is measured on answered invoices)")
    print(f"Field extraction accuracy:      {_pct(s['field_accuracy'])}")
    print(f"Correct final decision:         {_pct(s['status_accuracy'])}")
    print(f"Billing errors caught:          {_pct(s['errors_caught'])}")
    print(f"False alarms on good invoices:  {_pct(s['false_alarms'])}")
    print(f"Duplicates caught:              {_pct(s['duplicates_caught'])}")
    print(f"Injection attacks resisted:     {_pct(s['injections_resisted'])}")
    print(f"AI service failures:            {_pct(s['api_failures'])}")
    print(f"Average time per invoice:       {s['avg_seconds']} s")
    print("\nFull report saved to eval/results.md")
    sys.exit(0)
