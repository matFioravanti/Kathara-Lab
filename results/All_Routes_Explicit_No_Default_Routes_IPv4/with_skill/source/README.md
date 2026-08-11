# Five-router explicit IPv4 routing lab

This lab has five routers and five LANs. R1 connects to R2 and R3; both R2 and R3 connect to R4; R4 connects to R5. Every LAN contains two PCs. The routers use only specific IPv4 static routes and deliberately have no default route.

## Start

Run `kathara lstart` from this directory.

## Addressing

| LAN | Router | PCs |
| --- | --- | --- |
| 10.1.1.0/24 | R1: 10.1.1.1 | PC1A: 10.1.1.10, PC1B: 10.1.1.11 |
| 10.2.2.0/24 | R2: 10.2.2.1 | PC2A: 10.2.2.10, PC2B: 10.2.2.11 |
| 10.3.3.0/24 | R3: 10.3.3.1 | PC3A: 10.3.3.10, PC3B: 10.3.3.11 |
| 10.4.4.0/24 | R4: 10.4.4.1 | PC4A: 10.4.4.10, PC4B: 10.4.4.11 |
| 10.5.5.0/24 | R5: 10.5.5.1 | PC5A: 10.5.5.10, PC5B: 10.5.5.11 |

Router point-to-point links are 10.255.12.0/30, 10.255.13.0/30, 10.255.24.0/30, 10.255.34.0/30, and 10.255.45.0/30.

## Quick check

After starting the lab, run `kathara exec pc1a -- ping -c 2 10.5.5.11`. Inspect any router with `kathara exec r1 -- ip route show`; its table contains no `default` route.
