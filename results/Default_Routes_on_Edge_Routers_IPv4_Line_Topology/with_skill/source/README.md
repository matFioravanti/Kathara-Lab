# Default Routes on Edge Routers (IPv4)

This lab models four routers in the linear path `R1--R2--R3--R4`; each router connects to a LAN containing two PCs. R1 and R4 use a static default route toward the chain, while R2 and R3 use only explicit static routes to remote LANs.

## Addressing

| Segment | Network | Router address | PC addresses |
| --- | --- | --- | --- |
| R1 LAN | 192.168.10.0/24 | R1: 192.168.10.1 | pc11: .11, pc12: .12 |
| R2 LAN | 192.168.20.0/24 | R2: 192.168.20.1 | pc21: .11, pc22: .12 |
| R3 LAN | 192.168.30.0/24 | R3: 192.168.30.1 | pc31: .11, pc32: .12 |
| R4 LAN | 192.168.40.0/24 | R4: 192.168.40.1 | pc41: .11, pc42: .12 |
| R1--R2 | 10.0.12.0/30 | R1: 10.0.12.1, R2: 10.0.12.2 | — |
| R2--R3 | 10.0.23.0/30 | R2: 10.0.23.1, R3: 10.0.23.2 | — |
| R3--R4 | 10.0.34.0/30 | R3: 10.0.34.1, R4: 10.0.34.2 | — |

Start the laboratory with:

```sh
kathara lstart
```

For a quick end-to-end test, run `ping -c 2 192.168.40.12` from `pc11`. It should reach `pc42` through all four routers.
