# Five-router IPv4 static-routing laboratory

Start the laboratory from this directory with `kathara lstart`. Every router is configured by its matching `.startup` file and forwards IPv4 traffic. Each router has an explicit static route for each subnet that is not directly connected; no router installs a default route. PCs use their local router as their default gateway.

## Addressing

| Segment | IPv4 network | Addresses |
|---|---|---|
| LAN 1 | 10.0.1.0/24 | R1 10.0.1.1, PC1A 10.0.1.10, PC1B 10.0.1.11 |
| LAN 2 | 10.0.2.0/24 | R2 10.0.2.1, PC2A 10.0.2.10, PC2B 10.0.2.11 |
| LAN 3 | 10.0.3.0/24 | R3 10.0.3.1, PC3A 10.0.3.10, PC3B 10.0.3.11 |
| LAN 4 | 10.0.4.0/24 | R4 10.0.4.1, PC4A 10.0.4.10, PC4B 10.0.4.11 |
| LAN 5 | 10.0.5.0/24 | R5 10.0.5.1, PC5A 10.0.5.10, PC5B 10.0.5.11 |
| R1-R2 | 10.0.12.0/30 | R1 10.0.12.1, R2 10.0.12.2 |
| R1-R3 | 10.0.13.0/30 | R1 10.0.13.1, R3 10.0.13.2 |
| R2-R4 | 10.0.24.0/30 | R2 10.0.24.1, R4 10.0.24.2 |
| R3-R4 | 10.0.34.0/30 | R3 10.0.34.1, R4 10.0.34.2 |
| R4-R5 | 10.0.45.0/30 | R4 10.0.45.1, R5 10.0.45.2 |

The selected forwarding paths are symmetric for LAN traffic: R1 reaches LAN 4 and LAN 5 through R2; R2 reaches LAN 3 through R1; R4 reaches LAN 1 and LAN 2 through R2; R5 uses R4 for every remote subnet.
