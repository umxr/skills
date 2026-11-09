import argparse

from ledgerline.db.session import SessionLocal
from ledgerline.services.reconcile import reconcile_account


def main() -> None:
    p = argparse.ArgumentParser(prog="ledgerline")
    p.add_argument("account_id")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    with SessionLocal() as s:
        result = reconcile_account(s, a.account_id, dry_run=a.dry_run)
    print(result)


if __name__ == "__main__":
    main()
