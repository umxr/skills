package main

import (
	"log"
	"net/http"
	"os"

	"example.com/relay/auth"
	"example.com/relay/gateway/internal/proxy"
	"github.com/go-chi/chi/v5"
)

func main() {
	r := chi.NewRouter()
	r.Use(auth.Middleware(os.Getenv("AUTH_JWKS_URL")))
	r.Mount("/relay", proxy.Handler(os.Getenv("RELAY_ADDR")))
	log.Fatal(http.ListenAndServe(":8080", r))
}
