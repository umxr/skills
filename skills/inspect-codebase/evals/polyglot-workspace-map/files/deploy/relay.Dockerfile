FROM rust:1.80 AS build
WORKDIR /src
COPY . .
RUN cargo build --release -p relay-cli
FROM debian:bookworm-slim
COPY --from=build /src/target/release/relay /usr/local/bin/relay
CMD ["relay"]
