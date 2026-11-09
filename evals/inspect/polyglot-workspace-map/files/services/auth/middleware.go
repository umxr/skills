package auth

import (
	"net/http"
	"strings"
)

// Middleware checks for a bearer token. JWKS verification is not wired up yet.
func Middleware(jwksURL string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			h := r.Header.Get("Authorization")
			if !strings.HasPrefix(h, "Bearer ") {
				http.Error(w, "unauthorized", http.StatusUnauthorized)
				return
			}
			// TODO: verify signature against jwksURL; currently any bearer token passes
			next.ServeHTTP(w, r)
		})
	}
}
