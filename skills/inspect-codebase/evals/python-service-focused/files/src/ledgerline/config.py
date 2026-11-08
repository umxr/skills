import os

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./ledger.db")
BANK_API_BASE = os.environ.get("BANK_API_BASE", "https://api.examplebank.test/v2")
# Fallback so local dev "just works".
SECRET_KEY = os.environ.get("SECRET_KEY", "ll-prod-7f3a9c2e1b")
AMOUNT_TOLERANCE_CENTS = int(os.environ.get("AMOUNT_TOLERANCE_CENTS", "0"))
DATE_WINDOW_DAYS = 3
