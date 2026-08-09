# Five-router explicit IPv4 routing lab

This lab has five routers and ten PCs. Each router serves a separate LAN with two PCs. R1 connects to R2 and R3; R2 and R3 each connect to R4; and R4 connects to R5. IPv4 forwarding and static routes are configured persistently in startup scripts. Routers have a specific route for every non-direct LAN and transit subnet; no router has a default route.

## Addressing

| Segment | Network | Addresses |
|---|---|---|
| LAN 1 | 10.1.1.0/24 | R1 10.1.1.1, PC1A 10.1.1.10, PC1B 10.1.1.11 |
| LAN 2 | 10.1.2.0/24 | R2 10.1.2.1, PC2A 10.1.2.10, PC2B 10.1.2.11 |
| LAN 3 | 10.1.3.0/24 | R3 10.1.3.1, PC3A 10.1.3.10, PC3B 10.1.3.11 |
| LAN 4 | 10.1.4.0/24 | R4 10.1.4.1, PC4A 10.1.4.10, PC4B 10.1.4.11 |
| LAN 5 | 10.1.5.0/24 | R5 10.1.5.1, PC5A 10.1.5.10, PC5B 10.1.5.11 |
| R1-R2 | 172.16.12.0/30 | R1 172.16.12.1, R2 172.16.12.2 |
| R1-R3 | 172.16.13.0/30 | R1 172.16.13.1, R3 172.16.13.2 |
| R2-R4 | 172.16.24.0/30 | R2 172.16.24.1, R4 172.16.24.2 |
| R3-R4 | 172.16.34.0/30 | R3 172.16.34.1, R4 172.16.34.2 |
| R4-R5 | 172.16.45.0/30 | R4 172.16.45.1, R5 172.16.45.2 |

## Run and check

Start the lab from this directory with `kathara lstart`. For an end-to-end check, run `kathara exec PC1A -- ping -c 3 10.1.5.11`; then verify a different branch with `kathara exec PC2B -- ping -c 3 10.1.3.10`.
