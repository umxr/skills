package auth

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestRejectsMissingToken(t *testing.T) {
	h := Middleware("")(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {}))
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, httptest.NewRequest("GET", "/", nil))
	if rec.Code != http.StatusUnauthorized {
		t.Fatalf("got %d", rec.Code)
	}
}
