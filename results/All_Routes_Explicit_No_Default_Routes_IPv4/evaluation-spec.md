# Evaluation specification

## R1 — Router topology

The lab contains five routers: R1, R2, R3, R4, and R5.  Their inter-router connections are exactly:

- R1 connected to R2
- R1 connected to R3
- R2 connected to R4
- R3 connected to R4
- R4 connected to R5

## R2 — LANs and PCs

Each router serves one distinct LAN.  Each such LAN contains exactly two PCs, for a total of ten PCs.

## R3 — IP protocol version

The network uses IPv4 only.

## R4 — Explicit static routing

Every router has a fully explicit routing table.  For every subnet that is not directly connected to a router, that router has a specific static route to the subnet.

## R5 — No default routes

No router has a default route.

## R6 — End-to-end PC connectivity

Every one of the ten PCs can reach every other PC.
