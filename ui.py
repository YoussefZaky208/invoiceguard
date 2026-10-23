"""Look and feel for the InvoiceGuard app: theme colors, fonts and small HTML building blocks.

All text that comes from invoices is escaped before display, so a malicious invoice
can't inject HTML into the page.
"""

from html import escape

import core

# ---------- theme ----------
THEMES = {
    "light": {
        "bg": "#F1F4F3", "surface": "#FFFFFF", "surface-2": "#E6EBE9", "border": "#CDD5D2",
        "ink": "#17212B", "muted": "#4F5D68", "accent": "#0E6B5C", "accent-ink": "#FFFFFF",
        "ok": "#11733F", "ok-bg": "#E2F2E8", "warn": "#8F4300", "warn-bg": "#FCEFD9",
        "bad": "#B42318", "bad-bg": "#FCE7E4", "dup": "#5B3BB0", "dup-bg": "#EDE7FA",
        "focus": "#0B57D0",
    },
    "dark": {
        "bg": "#0F1519", "surface": "#172026", "surface-2": "#202B32", "border": "#33424B",
        "ink": "#E7ECEF", "muted": "#A3B1BA", "accent": "#43C2A8", "accent-ink": "#05231D",
        "ok": "#5BD08F", "ok-bg": "#123020", "warn": "#F3B355", "warn-bg": "#35260D",
        "bad": "#FF8A7A", "bad-bg": "#3B1814", "dup": "#C3A8FF", "dup-bg": "#271E3E",
        "focus": "#8AB4F8",
    },
}

FONTS = (
    "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800"
    "&family=Public+Sans:wght@400;500;600;700&display=swap"
)


def css(mode: str) -> str:
    tokens = "\n".join(f"  --{name}: {value};" for name, value in THEMES[mode].items())
    return f"""
<style>
@import url('{FONTS}');
:root {{
{tokens}
  --display: 'Bricolage Grotesque', 'Segoe UI', sans-serif;
  --text: 'Public Sans', 'Segoe UI', system-ui, sans-serif;
  color-scheme: {mode};
}}

/* ---- page ---- */
.stApp, [data-testid="stAppViewContainer"] {{ background: var(--bg); color: var(--ink); font-family: var(--text); }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stMainBlockContainer"], .block-container {{ max-width: 1240px; padding-top: 2.25rem; }}
.stApp [data-testid="stMarkdownContainer"], .stApp label, .stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stCaptionContainer"] {{ color: var(--ink); font-family: var(--text); }}
.stApp [data-testid="stMarkdownContainer"] p {{ font-size: 1rem; line-height: 1.55; }}
.stApp h1, .stApp h2, .stApp h3 {{ font-family: var(--display); color: var(--ink); letter-spacing: -0.01em; }}
[data-testid="stToolbar"] button, [data-testid="stMainMenu"] svg {{ color: var(--muted); }}

/* ---- sidebar ---- */
[data-testid="stSidebar"] {{ background: var(--surface); border-right: 1px solid var(--border); }}
[data-testid="stSidebarCollapseButton"] svg, [data-testid="stExpandSidebarButton"] svg {{ color: var(--muted); }}

/* ---- tabs ---- */
.stTabs [data-baseweb="tab-list"] {{ gap: 0.25rem; }}
.stTabs [data-baseweb="tab"] {{ color: var(--muted); font-weight: 600; padding: 0.6rem 0.9rem; min-height: 44px; }}
.stTabs [data-baseweb="tab"] p {{ font-size: 1rem; }}
.stTabs [data-baseweb="tab"][aria-selected="true"] {{ color: var(--ink); }}
.stTabs [data-baseweb="tab-highlight"] {{ background: var(--accent) !important; height: 3px; }}
.stTabs [data-baseweb="tab-border"] {{ background: var(--border); }}

/* ---- buttons ---- */
.stApp [data-testid^="stBaseButton"] {{
  min-height: 44px; border-radius: 10px; font-weight: 600; font-family: var(--text);
  background: var(--surface); color: var(--ink); border: 1px solid var(--border);
  transition: background-color .15s ease, border-color .15s ease;
}}
.stApp [data-testid^="stBaseButton"]:hover {{ border-color: var(--accent); color: var(--ink); background: var(--surface-2); }}
.stApp [data-testid="stBaseButton-primary"] {{ background: var(--accent); color: var(--accent-ink); border-color: var(--accent); }}
.stApp [data-testid="stBaseButton-primary"]:hover {{ background: var(--accent); color: var(--accent-ink); filter: brightness(1.08); }}
.stApp [data-testid^="stBaseButton"]:disabled {{ opacity: .5; }}
.stApp button [data-testid="stMarkdownContainer"], .stApp button p {{ color: inherit; font-weight: 600; }}
.stApp [class*="st-key-approve"] [data-testid^="stBaseButton"] {{ background: var(--ok-bg); color: var(--ok); border-color: var(--ok); }}
.stApp [class*="st-key-reject"] [data-testid^="stBaseButton"] {{ background: var(--bad-bg); color: var(--bad); border-color: var(--bad); }}

/* ---- form controls ---- */
.stApp [data-baseweb="select"] > div, .stApp [data-baseweb="input"], .stApp [data-baseweb="base-input"],
.stApp [data-testid="stChatInput"], .stApp [data-testid="stChatInput"] > div {{
  background: var(--surface); border-color: var(--border); color: var(--ink);
}}
.stApp input, .stApp textarea, .stApp [data-baseweb="select"] div {{ color: var(--ink); font-family: var(--text); }}
.stApp input::placeholder, .stApp textarea::placeholder {{ color: var(--muted); opacity: 1; }}
[data-baseweb="popover"] ul, [data-baseweb="popover"] li, [data-baseweb="menu"] {{ background: var(--surface); color: var(--ink); }}
[data-baseweb="popover"] li:hover, [data-baseweb="popover"] li[aria-selected="true"] {{ background: var(--surface-2); }}
.stApp [data-testid="stFileUploaderDropzone"] {{ background: var(--surface); border: 2px dashed var(--border); border-radius: 14px; }}
.stApp [data-testid="stFileUploaderDropzone"] * {{ color: var(--ink); }}
.stApp [data-testid="stFileUploaderDropzoneInstructions"] small {{ color: var(--muted); }}
.stApp [data-testid="stFileUploaderFile"] * {{ color: var(--ink); }}
.stApp [data-testid="stWidgetLabel"] p {{ font-weight: 600; }}

/* selectbox (combobox) and text inputs */
.stApp [data-testid="stSelectbox"] [role="group"], .stApp [data-testid="stTextInputRootElement"],
.stApp [data-testid="stTextInput"] [data-baseweb="input"] {{
  background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 10px; min-height: 44px;
}}
.stApp [data-testid="stSelectbox"] input, .stApp [data-testid="stTextInput"] input {{ background: transparent !important; color: var(--ink) !important; }}
.stApp [data-testid="stSelectbox"] button svg {{ color: var(--muted); }}
.react-aria-Popover, [role="listbox"] {{ background: var(--surface) !important; color: var(--ink) !important; border-color: var(--border) !important; }}
[role="listbox"] [role="option"] {{ color: var(--ink) !important; background: transparent; }}
[role="listbox"] [role="option"]:hover, [role="listbox"] [role="option"][data-focused], [role="listbox"] [role="option"][aria-selected="true"] {{ background: var(--surface-2) !important; }}

/* segmented controls and pills */
.stApp [data-testid="stButtonGroup"] button {{ background: var(--surface); color: var(--ink); border-color: var(--border); min-height: 40px; }}
.stApp [data-testid="stButtonGroup"] button[aria-checked="true"], .stApp [data-testid="stButtonGroup"] button[kind$="Active"] {{
  background: var(--accent); color: var(--accent-ink); border-color: var(--accent);
}}

/* expanders, chat, toasts */
.stApp [data-testid="stExpander"] details {{ background: var(--surface); border: 1px solid var(--border); border-radius: 14px; }}
.stApp [data-testid="stExpander"] summary {{ color: var(--ink) !important; background: var(--surface) !important; min-height: 52px; border-radius: 14px; }}
.stApp [data-testid="stExpander"] details[open] > summary {{ border-bottom: 1px solid var(--border); border-radius: 14px 14px 0 0; }}
.stApp [data-testid="stExpander"] summary p, .stApp [data-testid="stExpander"] summary span {{ color: var(--ink) !important; font-weight: 600; }}
.stApp [data-testid="stExpander"] summary:hover {{ color: var(--accent); }}
.stApp [data-testid="stExpander"] summary svg {{ color: var(--muted); }}
.stApp [data-testid="stChatMessage"] {{ background: transparent; }}
[data-testid="stToast"] {{ background: var(--surface); color: var(--ink); border: 1px solid var(--border); }}
.stApp [data-testid="stSpinner"] * {{ color: var(--ink); }}
.stApp [data-testid="stCheckbox"] label p, .stApp [data-testid="stToggle"] label p {{ color: var(--ink); }}
.stApp [data-testid="stImageCaption"] {{ color: var(--muted); }}

/* ---- keyboard focus: always visible ---- */
.stApp button:focus-visible, .stApp input:focus-visible, .stApp textarea:focus-visible,
.stApp summary:focus-visible, .stApp [role="tab"]:focus-visible, .stApp a:focus-visible, .stApp label:focus-within {{
  outline: 3px solid var(--focus) !important; outline-offset: 2px; border-radius: 8px;
}}

/* ---- InvoiceGuard components ---- */
.ig-brand {{ display: flex; align-items: center; gap: .75rem; }}
.ig-brand svg {{ flex: none; }}
.ig-brand h1 {{ font-size: 2.1rem; line-height: 1.1; margin: 0; padding: 0; font-weight: 750; }}
.ig-tagline {{ color: var(--muted); margin: .35rem 0 1.25rem; font-size: 1.05rem; }}

.ig-ledger {{ display: grid; gap: .25rem; margin: .5rem 0 1rem; }}
.ig-ledger-row {{ display: grid; grid-template-columns: auto 1fr; column-gap: .75rem; align-items: baseline;
  padding: .7rem 0; border-bottom: 1px solid var(--border); }}
.ig-ledger-row:last-child {{ border-bottom: 0; }}
.ig-ledger-count {{ font-family: var(--display); font-size: 2rem; font-weight: 700; line-height: 1;
  font-variant-numeric: tabular-nums; min-width: 2ch; text-align: right; }}
.ig-ledger-label {{ font-weight: 600; color: var(--ink); }}
.ig-ledger-amount {{ grid-column: 2; color: var(--muted); font-variant-numeric: tabular-nums; font-size: .95rem; }}
.ig-ledger-row.warn .ig-ledger-count {{ color: var(--warn); }}
.ig-ledger-row.ok .ig-ledger-count {{ color: var(--ok); }}
.ig-ledger-row.bad .ig-ledger-count {{ color: var(--bad); }}
.ig-side-note {{ color: var(--muted); font-size: .9rem; line-height: 1.5; margin: .25rem 0; }}
.ig-side-note a {{ color: var(--accent); }}
.ig-side-note code {{ background: var(--surface-2); color: var(--ink); padding: .05rem .35rem; border-radius: 5px; font-size: .85rem; white-space: nowrap; }}

.ig-chip {{ display: inline-flex; align-items: center; gap: .35rem; padding: .2rem .6rem; border-radius: 999px;
  font-weight: 600; font-size: .9rem; white-space: nowrap; border: 1px solid currentColor; }}
.ig-chip.ok {{ color: var(--ok); background: var(--ok-bg); }}
.ig-chip.warn {{ color: var(--warn); background: var(--warn-bg); }}
.ig-chip.bad {{ color: var(--bad); background: var(--bad-bg); }}
.ig-chip.dup {{ color: var(--dup); background: var(--dup-bg); }}

.ig-result-head {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; margin-bottom: 1rem; }}
.ig-result-head h2 {{ font-size: 1.6rem; line-height: 1.2; margin: 0 0 .5rem; padding: 0; }}
.ig-facts {{ display: grid; grid-template-columns: auto 1fr; gap: .2rem 1rem; margin: 0; font-size: .97rem; }}
.ig-facts dt {{ color: var(--muted); }}
.ig-facts dd {{ margin: 0; font-variant-numeric: tabular-nums; }}

.ig-stamp {{ flex: none; font-family: var(--display); font-weight: 800; font-size: 1.05rem; letter-spacing: .12em;
  text-transform: uppercase; padding: .45rem .8rem; border: 4px double currentColor; border-radius: 8px;
  transform: rotate(-6deg); text-align: center; line-height: 1.15; margin-top: .4rem;
  animation: ig-stamp .45s cubic-bezier(.2, 1.6, .4, 1) both; }}
.ig-stamp small {{ display: block; font-family: var(--text); font-weight: 600; font-size: .7rem; letter-spacing: .04em; }}
.ig-stamp.ok {{ color: var(--ok); }} .ig-stamp.warn {{ color: var(--warn); }}
.ig-stamp.bad {{ color: var(--bad); }} .ig-stamp.dup {{ color: var(--dup); }}
@keyframes ig-stamp {{ from {{ opacity: 0; transform: rotate(-6deg) scale(1.6); }} to {{ opacity: 1; transform: rotate(-6deg) scale(1); }} }}
@media (prefers-reduced-motion: reduce) {{ .ig-stamp {{ animation: none; }} }}

.ig-note {{ border-radius: 12px; padding: .85rem 1rem; margin: .5rem 0 1rem; border: 1px solid currentColor; line-height: 1.5; }}
.ig-note strong {{ display: block; margin-bottom: .2rem; }}
.ig-note ul {{ margin: .3rem 0 0; padding-left: 1.2rem; }}
.ig-note li {{ margin: .15rem 0; }}
.ig-note.ok {{ color: var(--ok); background: var(--ok-bg); }}
.ig-note.warn {{ color: var(--warn); background: var(--warn-bg); }}
.ig-note.bad {{ color: var(--bad); background: var(--bad-bg); }}
.ig-note.dup {{ color: var(--dup); background: var(--dup-bg); }}
.ig-note.info {{ color: var(--ink); background: var(--surface); border-color: var(--border); }}

.ig-table-wrap {{ overflow-x: auto; border: 1px solid var(--border); border-radius: 12px; background: var(--surface); margin: .25rem 0 1rem; }}
.ig-table {{ width: 100%; border-collapse: collapse; font-size: .97rem; color: var(--ink); }}
.ig-table caption {{ text-align: left; padding: .7rem .9rem .2rem; color: var(--muted); font-size: .9rem; }}
.ig-table th {{ text-align: left; font-weight: 600; color: var(--muted); background: var(--surface-2); padding: .6rem .9rem; white-space: nowrap; }}
.stApp .ig-table th, .stApp .ig-table td {{ border: 0; }}
.stApp .ig-table td {{ padding: .6rem .9rem; border-top: 1px solid var(--border); vertical-align: top; }}
.ig-table .nw {{ white-space: nowrap; }}
.ig-table .num {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
.ig-table tr.flag td {{ background: var(--bad-bg); }}
.ig-table tr.flag td:first-child {{ box-shadow: inset 4px 0 0 var(--bad); }}
.ig-fix {{ display: block; color: var(--bad); font-weight: 600; font-size: .88rem; }}
.ig-table tfoot td {{ border-top: 1px solid var(--border); }}
.ig-table tfoot tr.grand td {{ font-weight: 700; font-size: 1.05rem; }}

.ig-steps {{ display: grid; gap: .9rem; margin: 1rem 0 0; padding: 0; list-style: none; counter-reset: step; }}
.ig-steps li {{ counter-increment: step; display: grid; grid-template-columns: 2.2rem 1fr; gap: .75rem; align-items: start; }}
.ig-steps li::before {{ content: counter(step); font-family: var(--display); font-weight: 700; width: 2.2rem; height: 2.2rem;
  border-radius: 50%; display: grid; place-items: center; background: var(--surface-2); color: var(--accent); }}
.ig-steps strong {{ display: block; }}
.ig-steps span {{ color: var(--muted); }}
.ig-empty {{ padding: 2rem 1.25rem; text-align: center; border: 2px dashed var(--border); border-radius: 14px; color: var(--muted); }}
.ig-empty strong {{ display: block; color: var(--ink); font-size: 1.1rem; margin-bottom: .25rem; }}
.ig-section-title {{ font-family: var(--display); font-size: 1.5rem; font-weight: 700; margin: .5rem 0 .25rem; color: var(--ink); }}
.ig-section-sub {{ color: var(--muted); margin: 0 0 1rem; }}
</style>
"""


# ---------- small building blocks ----------
STATUS = {
    "approved": ("ok", "✓", "Approved"),
    "needs_review": ("warn", "!", "Needs review"),
    "rejected": ("bad", "✕", "Rejected"),
    "duplicate": ("dup", "⧉", "Already received"),
}


def money(value: float, currency: str = "EGP") -> str:
    return f"{value:,.2f} {escape(currency or '')}".strip()


def chip(status: str) -> str:
    tone, icon, label = STATUS[status]
    return f'<span class="ig-chip {tone}"><span aria-hidden="true">{icon}</span>{label}</span>'


def brand() -> str:
    mark = (
        '<svg width="44" height="44" viewBox="0 0 44 44" aria-hidden="true">'
        '<rect x="6" y="4" width="28" height="36" rx="4" fill="var(--surface)" stroke="var(--ink)" stroke-width="2.5"/>'
        '<path d="M12 13h16M12 19h16M12 25h9" stroke="var(--muted)" stroke-width="2.5" stroke-linecap="round"/>'
        '<circle cx="31" cy="31" r="9" fill="var(--accent)"/>'
        '<path d="M27 31.2l2.8 2.8 5-5.4" stroke="var(--accent-ink)" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        "</svg>"
    )
    return (
        f'<div class="ig-brand">{mark}<h1>InvoiceGuard</h1></div>'
        '<p class="ig-tagline">Check supplier invoices before you pay them.</p>'
    )


def ledger(invoices: list[dict]) -> str:
    rows = []
    for status, tone, label in (("needs_review", "warn", "Waiting for review"), ("approved", "ok", "Approved"),
                                ("rejected", "bad", "Rejected")):
        items = [i for i in invoices if i["status"] == status]
        amount = sum(i["total"] for i in items)
        rows.append(
            f'<div class="ig-ledger-row {tone}"><span class="ig-ledger-count">{len(items)}</span>'
            f'<span class="ig-ledger-label">{label}</span>'
            f'<span class="ig-ledger-amount">{money(amount)}</span></div>'
        )
    return f'<div class="ig-ledger" role="list" aria-label="Invoice totals">{"".join(rows)}</div>'


def stamp(status: str, when: str = "") -> str:
    tone, _, label = STATUS[status]
    date = f"<small>{escape(when)}</small>" if when else ""
    return f'<div class="ig-stamp {tone}" role="img" aria-label="Status: {label}">{label}{date}</div>'


def result_header(invoice: dict, status: str, invoice_id: int, when: str = "") -> str:
    facts = [
        ("Invoice", escape(invoice["invoice_number"]) or "<em>missing</em>"),
        ("Dated", escape(invoice["invoice_date"]) or "<em>missing</em>"),
        ("Total", money(invoice["total"], invoice["currency"])),
        ("Record", f"#{invoice_id}"),
    ]
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts)
    return (
        f'<div class="ig-result-head"><div><h2>{escape(invoice["supplier"]) or "Unknown supplier"}</h2>'
        f'<dl class="ig-facts">{dl}</dl></div>{stamp(status, when)}</div>'
    )


def note(tone: str, title: str, items: list[str] | None = None, text: str = "") -> str:
    body = f"<p style='margin:0'>{escape(text)}</p>" if text else ""
    if items:
        body += "<ul>" + "".join(f"<li>{escape(i)}</li>" for i in items) + "</ul>"
    role = ' role="alert"' if tone == "bad" else ""
    return f'<div class="ig-note {tone}"{role}><strong>{escape(title)}</strong>{body}</div>'


def line_items_table(invoice: dict) -> str:
    """Invoice lines with any wrong line highlighted and the correct figure shown next to it."""
    cur = invoice["currency"]
    rows = []
    for li in invoice["line_items"]:
        expected = round(li["quantity"] * li["unit_price"], 2)
        wrong = abs(expected - li["amount"]) > core.TOLERANCE
        fix = f'<span class="ig-fix"><span aria-hidden="true">! </span>Should be {expected:,.2f}</span>' if wrong else ""
        rows.append(
            f'<tr class="{"flag" if wrong else ""}"><td>{escape(li["description"])}</td>'
            f'<td class="num">{li["quantity"]:g}</td><td class="num">{li["unit_price"]:,.2f}</td>'
            f'<td class="num">{li["amount"]:,.2f}{fix}</td></tr>'
        )

    items_sum = round(sum(li["amount"] for li in invoice["line_items"]), 2)
    expected_total = round(invoice["subtotal"] + invoice["tax"], 2)
    sub_wrong = bool(invoice["line_items"]) and abs(items_sum - invoice["subtotal"]) > core.TOLERANCE
    total_wrong = abs(expected_total - invoice["total"]) > core.TOLERANCE

    def foot(label, value, wrong, should, grand=False):
        fix = f'<span class="ig-fix"><span aria-hidden="true">! </span>Should be {should:,.2f}</span>' if wrong else ""
        cls = " ".join(c for c in ("flag" if wrong else "", "grand" if grand else "") if c)
        return f'<tr class="{cls}"><td colspan="3">{label}</td><td class="num">{value:,.2f}{fix}</td></tr>'

    return (
        '<div class="ig-table-wrap"><table class="ig-table">'
        f"<caption>Line items in {escape(cur)}. Highlighted rows don't add up.</caption>"
        '<thead><tr><th scope="col">Description</th><th scope="col" class="num">Qty</th>'
        '<th scope="col" class="num">Unit price</th><th scope="col" class="num">Amount</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody><tfoot>'
        + foot("Subtotal", invoice["subtotal"], sub_wrong, items_sum)
        + foot("Tax", invoice["tax"], False, 0)
        + foot(f"Total ({escape(cur)})", invoice["total"], total_wrong, expected_total, grand=True)
        + "</tfoot></table></div>"
    )


def invoices_table(invoices: list[dict]) -> str:
    rows = "".join(
        f'<tr><td class="num">{i["id"]}</td><td>{escape(i["supplier"])}</td>'
        f'<td class="nw">{escape(i["invoice_number"]) or "<em>missing</em>"}</td><td class="nw">{escape(i["invoice_date"])}</td>'
        f'<td class="num">{money(i["total"], i["currency"])}</td><td>{chip(i["status"])}</td>'
        f'<td class="nw">{escape((i["reviewed_at"] or "")[:16].replace("T", " ")) or "Automatic"}</td></tr>'
        for i in invoices
    )
    return (
        '<div class="ig-table-wrap"><table class="ig-table">'
        '<thead><tr><th scope="col" class="num">#</th><th scope="col">Supplier</th><th scope="col">Invoice</th>'
        '<th scope="col">Date</th><th scope="col" class="num">Total</th><th scope="col">Status</th>'
        f'<th scope="col">Decided</th></tr></thead><tbody>{rows}</tbody></table></div>'
    )


def how_it_works() -> str:
    return (
        '<ol class="ig-steps">'
        "<li><div><strong>The AI reads the invoice</strong><span>Supplier, number, date and every line, copied exactly as printed.</span></div></li>"
        "<li><div><strong>Rules check the math</strong><span>Each line, the subtotal and the total, plus a check for invoices already received.</span></div></li>"
        "<li><div><strong>You decide on anything flagged</strong><span>Correct invoices are approved automatically. Problems wait for a person.</span></div></li>"
        "</ol>"
    )


def empty(title: str, text: str) -> str:
    return f'<div class="ig-empty"><strong>{escape(title)}</strong>{escape(text)}</div>'


def section(title: str, sub: str = "") -> str:
    subtitle = f'<p class="ig-section-sub">{escape(sub)}</p>' if sub else ""
    return f'<h2 class="ig-section-title">{escape(title)}</h2>{subtitle}'
