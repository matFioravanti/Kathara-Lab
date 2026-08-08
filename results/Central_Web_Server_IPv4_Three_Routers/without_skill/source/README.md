# Three-router IPv4 static-routing laboratory

This Kathara laboratory connects two client machines on a left LAN to an HTTP
server on a right LAN through three routers in a line.  `r2` is a pure transit
router and has no end-user devices.  IPv4 forwarding and every non-connected
route are configured in the node startup files; no dynamic-routing protocol is
used.

## Topology

```
client1 192.168.10.11 ─┐
client2 192.168.10.12 ─┼─ left_lan ─ r1 ─ r1_r2 ─ r2 ─ r2_r3 ─ r3 ─ server_lan ─ web 192.168.30.80:80
                       └───────────────┘
```

## Addressing

| Node | Interface | IPv4 address |
|---|---|---|
| client1 | eth0 | 192.168.10.11/24 |
| client2 | eth0 | 192.168.10.12/24 |
| r1 | eth0 / eth1 | 192.168.10.1/24 / 10.0.12.1/30 |
| r2 | eth0 / eth1 | 10.0.12.2/30 / 10.0.23.1/30 |
| r3 | eth0 / eth1 | 10.0.23.2/30 / 192.168.30.1/24 |
| web | eth0 | 192.168.30.80/24 |

The edge nodes use default routes toward their adjacent router.  The middle
router uses explicit static routes for `192.168.10.0/24` via `10.0.12.1` and
`192.168.30.0/24` via `10.0.23.2`.

## Use

From this directory, start the lab with `kathara lstart`.  After all nodes are
up, verify end-to-end routing and HTTP from either client:

```sh
kathara exec client1 -- ping -c 3 192.168.30.80
kathara exec client1 -- wget -qO- http://192.168.30.80/
kathara exec client2 -- wget -qO- http://192.168.30.80/
```

The HTTP response contains `IPv4 static routing is working.`  Stop the
laboratory with `kathara lclean` when finished.
