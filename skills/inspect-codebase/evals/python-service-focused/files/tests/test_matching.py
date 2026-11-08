from datetime import date
from types import SimpleNamespace

from ledgerline.services.matching import extract_reference, score


def test_extract_reference():
    assert extract_reference("Payment INV 12345 thanks") == "INV-12345"
    assert extract_reference("no ref") is None


def test_score_exact():
    line = SimpleNamespace(description="INV-1001", amount_cents=500, booked_on=date(2024, 1, 2))
    inv = SimpleNamespace(reference="INV-1001", amount_cents=500, due_date=date(2024, 1, 1))
    assert score(line, inv) == 100
