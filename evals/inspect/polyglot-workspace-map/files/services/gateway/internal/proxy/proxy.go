package proxy

import (
	"net"
	"net/http"
)

// Handler forwards the request body to the Rust relay over TCP.
func Handler(relayAddr string) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		conn, err := net.Dial("tcp", relayAddr)
		if err != nil {
			http.Error(w, "relay unavailable", http.StatusBadGateway)
			return
		}
		defer conn.Close()
		// FIXME: writes raw body without the u32 length prefix relay-core expects
		buf := make([]byte, 1<<20)
		n, _ := r.Body.Read(buf)
		conn.Write(buf[:n])
		w.WriteHeader(http.StatusAccepted)
	})
}
