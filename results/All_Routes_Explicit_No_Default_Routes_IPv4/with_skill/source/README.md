# Five-router explicit IPv4 static routing

This lab has five routers, each serving a LAN with two PCs. R1 connects to R2 and R3; R2 and R3 both connect to R4; R4 connects to R5. IPv4 routing on every router is fully explicit: each non-directly-connected LAN and transit subnet has a dedicated static route, and no router has a default route.

## Addressing

| Segment | IPv4 subnet | Router address(es) |
| --- | --- | --- |
| LAN 1 | 10.1.1.0/24 | R1: 10.1.1.1 |
| LAN 2 | 10.2.2.0/24 | R2: 10.2.2.1 |
| LAN 3 | 10.3.3.0/24 | R3: 10.3.3.1 |
| LAN 4 | 10.4.4.0/24 | R4: 10.4.4.1 |
| LAN 5 | 10.5.5.0/24 | R5: 10.5.5.1 |
| R1--R2 | 10.255.12.0/30 | R1: .1, R2: .2 |
| R1--R3 | 10.255.13.0/30 | R1: .1, R3: .2 |
| R2--R4 | 10.255.24.0/30 | R2: .1, R4: .2 |
| R3--R4 | 10.255.34.0/30 | R3: .1, R4: .2 |
| R4--R5 | 10.255.45.0/30 | R4: .1, R5: .2 |

Each LAN's PCs use addresses `.10` and `.11` and their local router (`.1`) as the default gateway.

## Run and test

Start the lab from this directory:

```sh
kathara lstart
```

For example, verify end-to-end reachability with:

```sh
kathara exec pc1a -- ping -c 3 10.5.5.11
```

Router routes can be inspected with `kathara exec r1 -- ip route show`; no router route table should contain a `default` entry.
