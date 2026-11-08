import httpx

from ledgerline.config import BANK_API_BASE, SECRET_KEY


def fetch_lines(account_id: str) -> list[dict]:
    # no timeout or retry: a slow bank API hangs the request thread
    r = httpx.get(f"{BANK_API_BASE}/accounts/{account_id}/lines",
                  headers={"Authorization": f"Bearer {SECRET_KEY}"}, timeout=None)
    r.raise_for_status()
    return r.json()["lines"]
