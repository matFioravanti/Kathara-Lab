# Three routers, IPv4 static routing, and HTTP

Two clients on the left LAN access an Apache web server on the right LAN through routers `r1`, `r2`, and `r3`. All addressing and routes are configured statically; IPv6 is disabled for every device.

## Topology and addressing

```text
pc1 (192.168.10.10) --\
                         LAN 192.168.10.0/24 -- r1 -- 10.0.12.0/30 -- r2 -- 10.0.23.0/30 -- r3 -- 192.168.30.0/24 -- web (192.168.30.10)
pc2 (192.168.10.11) --/
```

Start the laboratory from this directory:

```sh
kathara lstart
```

From either client, confirm the application path:

```sh
kathara exec pc1 -- curl http://192.168.30.10/
```
