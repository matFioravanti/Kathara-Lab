# Five routers, static routing, hierarchical DNS, and web server

Start the lab with `kathara lstart`. The client uses the local recursive resolver at `10.0.50.4`; that resolver follows the root service (`10.0.50.2`) to the authoritative `.org` service (`10.0.50.3`) to resolve `kathara.org` as `10.0.60.10`.

From the client, verify the service with `getent hosts kathara.org` and `curl http://kathara.org`.
