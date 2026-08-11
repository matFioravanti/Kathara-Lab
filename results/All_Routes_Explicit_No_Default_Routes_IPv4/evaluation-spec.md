# Evaluation specification

## Devices and topology

- The lab contains exactly five routers, designated R1, R2, R3, R4, and R5.
- R1 has a direct router-to-router connection to R2 and a direct router-to-router connection to R3.
- R2 has a direct router-to-router connection to R4.
- R3 has a direct router-to-router connection to R4.
- R4 has a direct router-to-router connection to R5.
- Each router serves exactly one LAN.
- Each router LAN contains exactly two PCs.
- The lab therefore contains exactly ten PCs.

## Network layer and routing

- The lab uses IPv4 only.
- Every router has a fully explicit routing table.
- On every router, there is a specific static route for every remote subnet.
- No router has a default route.

## Connectivity

- Every PC can reach each of the other nine PCs.
