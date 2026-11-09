from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ledgerline.db.session import get_session
from ledgerline.services.reconcile import reconcile_account

router = APIRouter()


@router.post("/accounts/{account_id}/reconcile")
def run_reconcile(account_id: str, dry_run: bool = False, s: Session = Depends(get_session)):
    return reconcile_account(s, account_id, dry_run=dry_run)


@router.get("/health")
def health():
    return {"ok": True}
