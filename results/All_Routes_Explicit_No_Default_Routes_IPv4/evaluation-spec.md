# Evaluation Specification

## Topology and devices

1. The scenario is a Kathara lab containing exactly five routers, identified by the roles R1, R2, R3, R4, and R5.
2. The router-to-router topology has these links: R1--R2, R1--R3, R2--R4, R3--R4, and R4--R5.
3. Each router serves one distinct LAN.
4. Each router LAN contains exactly two PCs, for a total of ten PCs.

## Network layer

5. The scenario uses IPv4 only.

## Routing

6. Every router has a fully explicit routing table.
7. On every router, every remote subnet has a specific static route.
8. No router has a default route.

## End-to-end connectivity

9. Every PC can reach every other PC.
