# Three routers, static IPv4 routing

This lab has the following topology:

```
client1 (192.168.10.11) --\
                            left_lan -- r1 -- r1_r2 -- r2 -- r2_r3 -- r3 -- server_lan -- web (192.168.30.10)
client2 (192.168.10.12) --/
```

## Addressing

| Segment | Network | Addresses |
|---|---|---|
| `left_lan` | `192.168.10.0/24` | r1 `192.168.10.1`, client1 `192.168.10.11`, client2 `192.168.10.12` |
| `r1_r2` | `10.0.12.0/30` | r1 `10.0.12.1`, r2 `10.0.12.2` |
| `r2_r3` | `10.0.23.0/30` | r2 `10.0.23.1`, r3 `10.0.23.2` |
| `server_lan` | `192.168.30.0/24` | r3 `192.168.30.1`, web `192.168.30.10` |

All routing is manually configured in the node startup scripts. R1 and R3 use a static default route toward R2; R2 has explicit static routes to both LANs. No IPv6 addressing or dynamic routing protocol is configured.

## Test

Start the laboratory from this directory with `kathara lstart`. Then, from either client, run:

```sh
curl http://192.168.30.10/
```

The command returns the page served by `web` on TCP port 80. `ping 192.168.30.10` and `traceroute -n 192.168.30.10` can be used to inspect connectivity and the three-router path.
