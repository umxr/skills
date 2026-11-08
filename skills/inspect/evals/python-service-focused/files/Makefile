.PHONY: run test lint migrate

run:
	uvicorn ledgerline.main:app --reload --port 8080

test:
	pytest -q

lint:
	ruff check src tests

migrate:
	alembic upgrade head
