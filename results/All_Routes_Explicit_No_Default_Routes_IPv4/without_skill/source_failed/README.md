# Five-router IPv4 static-routing laboratory

The lab contains five routers and ten PCs (two PCs on each router LAN). All router routes are explicit IPv4 static routes; no router uses a default route. PCs use their directly attached router as their default gateway.

## Addressing

| Link or LAN | IPv4 subnet |
|---|---|
| R1--R2 | 10.0.12.0/30 |
| R1--R3 | 10.0.13.0/30 |
| R2--R4 | 10.0.24.0/30 |
| R3--R4 | 10.0.34.0/30 |
| R4--R5 | 10.0.45.0/30 |
| R1 LAN through R5 LAN | 192.168.1.0/24 through 192.168.5.0/24 |
