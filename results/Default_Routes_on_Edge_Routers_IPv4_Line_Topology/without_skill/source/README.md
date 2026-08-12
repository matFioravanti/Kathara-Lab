# IPv4 line topology

This lab contains routers `R1`--`R4` and two PCs on each router LAN.

| LAN | Router gateway | PCs |
| --- | --- | --- |
| `192.168.10.0/24` | R1: `192.168.10.1` | PC11: `.11`, PC12: `.12` |
| `192.168.20.0/24` | R2: `192.168.20.1` | PC21: `.11`, PC22: `.12` |
| `192.168.30.0/24` | R3: `192.168.30.1` | PC31: `.11`, PC32: `.12` |
| `192.168.40.0/24` | R4: `192.168.40.1` | PC41: `.11`, PC42: `.12` |

The router transit networks are `10.0.12.0/30`, `10.0.23.0/30`, and
`10.0.34.0/30`. R1 and R4 use a default route toward the only neighbouring
router. R2 and R3 have no default route; each instead has an explicit static
route to every remote LAN.
