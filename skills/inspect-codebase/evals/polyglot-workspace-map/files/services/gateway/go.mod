module example.com/relay/gateway

go 1.22

require (
	example.com/relay/auth v0.0.0
	github.com/go-chi/chi/v5 v5.0.12
)

replace example.com/relay/auth => ../auth
