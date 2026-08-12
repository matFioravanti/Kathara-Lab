# Dual-stack partial mesh DNS and web lab

This laboratory uses six statically routed routers in a partial mesh. The client on R1 uses the local recursive DNS server, which forwards to a root server that delegates through `.net` to the authoritative `example.net` server on R4. `example.net` resolves to the dual-stack web server on R4.

Start the lab with `kathara lstart` from this directory. From `client`, validate both families with `getent ahostsv4 example.net`, `getent ahostsv6 example.net`, `curl -4 http://example.net`, and `curl -6 http://example.net`.
