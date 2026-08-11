# Five-router explicit IPv4 static routing lab

This lab has five routers and five LANs. R1 is linked to R2 and R3; R2 and R3 are each linked to R4; R4 is linked to R5. Each LAN contains its router plus two PCs. Router startup scripts enable IPv4 forwarding and install individual static routes for every non-directly connected LAN and transit subnet. No router installs a default route.

Start the lab with `kathara lstart` from this directory. For a quick end-to-end check after startup, run `kathara exec pc1a -- ping -c 2 10.5.5.12` and repeat with the source and destination reversed.

## Addressing

| Segment | IPv4 network | Addresses |
| --- | --- | --- |
| LAN 1 | 10.1.1.0/24 | R1 10.1.1.1; PC1A 10.1.1.11; PC1B 10.1.1.12 |
| LAN 2 | 10.2.2.0/24 | R2 10.2.2.1; PC2A 10.2.2.11; PC2B 10.2.2.12 |
| LAN 3 | 10.3.3.0/24 | R3 10.3.3.1; PC3A 10.3.3.11; PC3B 10.3.3.12 |
| LAN 4 | 10.4.4.0/24 | R4 10.4.4.1; PC4A 10.4.4.11; PC4B 10.4.4.12 |
| LAN 5 | 10.5.5.0/24 | R5 10.5.5.1; PC5A 10.5.5.11; PC5B 10.5.5.12 |
| R1-R2 | 172.16.12.0/30 | R1 172.16.12.1; R2 172.16.12.2 |
| R1-R3 | 172.16.13.0/30 | R1 172.16.13.1; R3 172.16.13.2 |
| R2-R4 | 172.16.24.0/30 | R2 172.16.24.1; R4 172.16.24.2 |
| R3-R4 | 172.16.34.0/30 | R3 172.16.34.1; R4 172.16.34.2 |
| R4-R5 | 172.16.45.0/30 | R4 172.16.45.1; R5 172.16.45.2 |
