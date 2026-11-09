.PHONY: all rust go test

all: rust go

rust:
	cargo build --workspace

go:
	cd services/gateway && go build ./...

test:
	cargo test --workspace
	cd services/gateway && go test ./...
