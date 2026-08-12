# Five-router explicit IPv4 routing lab

This lab has five routers and five two-host LANs. It demonstrates end-to-end IPv4 connectivity using only explicit static routes on the routers; no router has a default route.

## Topology and addressing

- R1: LAN1 `10.1.1.0/24`, R1-R2 `10.0.12.0/30`, R1-R3 `10.0.13.0/30`
- R2: LAN2 `10.2.2.0/24`, R2-R4 `10.0.24.0/30`
- R3: LAN3 `10.3.3.0/24`, R3-R4 `10.0.34.0/30`
- R4: LAN4 `10.4.4.0/24`, R4-R5 `10.0.45.0/30`
- R5: LAN5 `10.5.5.0/24`

Each LAN router uses address `.1`; the two PCs use `.10` and `.11`.

## Run and verify

Start the lab with `kathara lstart`. For a quick end-to-end check, run `kathara exec pc1a -- ping -c 2 10.5.5.11`.
