"""Reconciliation: pull bank lines, match them to open invoices, mark invoices paid.

Called from the HTTP API (api/routes.py) and the CLI (cli.py).
"""
from datetime import datetime

from sqlalchemy.orm import Session

from ledgerline.db.models import BankLine, Invoice
from ledgerline.integrations.bank_client import fetch_lines
from ledgerline.services.matching import score

MATCH_THRESHOLD = 60  # TODO: make configurable per account


def _upsert_lines(s: Session, account_id: str) -> list[BankLine]:
    out = []
    for raw in fetch_lines(account_id):
        line = s.get(BankLine, raw["id"])
        if line is None:
            line = BankLine(
                id=raw["id"],
                account_id=account_id,
                description=raw.get("description", ""),
                amount_cents=int(round(float(raw["amount"]) * 100)),
                booked_on=datetime.strptime(raw["booked_on"], "%Y-%m-%d").date(),
            )
            s.add(line)
        out.append(line)
    return out


def reconcile_account(s: Session, account_id: str, dry_run: bool = False) -> dict:
    lines = _upsert_lines(s, account_id)
    invoices = s.query(Invoice).filter_by(account_id=account_id, status="open").all()
    matched, unmatched = [], []
    for line in lines:
        if line.matched_invoice_id:
            continue
        best, best_score = None, 0
        for inv in invoices:
            sc = score(line, inv)
            # FIXME: ties go to whichever invoice comes first from the query (no ORDER BY)
            if sc > best_score:
                best, best_score = inv, sc
        if best is not None and best_score >= MATCH_THRESHOLD:
            matched.append((line.id, best.id, best_score))
            if not dry_run:
                line.matched_invoice_id = best.id
                best.status = "paid"
                # the same invoice can still be matched by a later line in this loop
        else:
            unmatched.append(line.id)
    if not dry_run:
        s.commit()
    return {"matched": matched, "unmatched": unmatched}
