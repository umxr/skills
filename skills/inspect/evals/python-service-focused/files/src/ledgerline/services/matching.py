"""Scoring helpers used by reconcile.py."""
import re
from datetime import date

from ledgerline.config import AMOUNT_TOLERANCE_CENTS, DATE_WINDOW_DAYS

REF_RE = re.compile(r"\bINV[- ]?(\d{4,})\b", re.I)


def extract_reference(description: str) -> str | None:
    m = REF_RE.search(description or "")
    return f"INV-{m.group(1)}" if m else None


def amount_matches(line_cents: int, invoice_cents: int) -> bool:
    return abs(line_cents - invoice_cents) <= AMOUNT_TOLERANCE_CENTS


def within_window(booked: date, due: date) -> bool:
    return abs((booked - due).days) <= DATE_WINDOW_DAYS


def score(line, invoice) -> int:
    s = 0
    if extract_reference(line.description) == invoice.reference:
        s += 50
    if amount_matches(line.amount_cents, invoice.amount_cents):
        s += 40
    if within_window(line.booked_on, invoice.due_date):
        s += 10
    return s
