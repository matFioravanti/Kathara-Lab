# Kathara Lab Implementation Prompt — Scenario 01, Version A

Create the Kathara lab `two_router_ipv4_static_routing_basics` at:

`prompts_generates/two_router_ipv4_static_routing_basics_01_version_A/two_router_ipv4_static_routing_basics/`

## Objective

Build an IPv4-only static-routing lab with two routers joined by one point-to-point link. Each router serves a separate LAN containing two PCs. Every PC must be able to ping every PC on the remote LAN. Do not configure dynamic routing protocols or default routes on the routers.

## Assumptions and conventions

- Use `kathara/core:latest` for all six devices.
- Name the routers `r1` and `r2`; name the PCs `pc1`, `pc2`, `pc3`, and `pc4`.
- Use `/24` masks for LANs and a `/30` mask for the router-to-router link.
- Use the `ip` command for all address and route configuration.
- Disable IPv6 in the lab configuration so the scenario is IPv4 only.

## Devices and addressing

| Device | Interface | Address | Purpose |
|---|---|---|---|
| r1 | eth0 | 192.168.10.1/24 | LAN 1 gateway |
| r1 | eth1 | 10.0.12.1/30 | Point-to-point link to r2 |
| r2 | eth0 | 10.0.12.2/30 | Point-to-point link to r1 |
| r2 | eth1 | 192.168.20.1/24 | LAN 2 gateway |
| pc1 | eth0 | 192.168.10.11/24 | LAN 1 host |
| pc2 | eth0 | 192.168.10.12/24 | LAN 1 host |
| pc3 | eth0 | 192.168.20.11/24 | LAN 2 host |
| pc4 | eth0 | 192.168.20.12/24 | LAN 2 host |

## Topology

- Collision domain `lan1`: `r1[0]`, `pc1[0]`, `pc2[0]`.
- Collision domain `r1_r2`: `r1[1]`, `r2[0]`.
- Collision domain `lan2`: `r2[1]`, `pc3[0]`, `pc4[0]`.
- Interface indexes in `lab.conf` must be contiguous and match the startup scripts.

## Required routing

- On `r1`, add the explicit static route `192.168.20.0/24 via 10.0.12.2`.
- On `r2`, add the explicit static route `192.168.10.0/24 via 10.0.12.1`.
- On `pc1` and `pc2`, add a default route via `192.168.10.1`.
- On `pc3` and `pc4`, add a default route via `192.168.20.1`.
- Do not add a default route on either router. Directly connected routes must remain implicit.

## Files to create

- `lab.conf`, defining the six devices, their images, the three collision domains, and IPv6 disabled.
- `r1.startup`, `r2.startup`, `pc1.startup`, `pc2.startup`, `pc3.startup`, and `pc4.startup`, each containing its persistent interface and route configuration.
- `README.md`, explaining the objective, topology, address plan, `kathara lstart`, and a short validation procedure.

## Acceptance checks

After the lab is created, run the following separately from the lab directory:

1. `kathara check`
2. `kathara lstart`
3. `kathara linfo`
4. Inspect addresses and routes with `kathara exec <device> -- ip addr show` and `kathara exec <device> -- ip route show` for each router and PC.
5. From `pc1`, ping `192.168.20.11` and `192.168.20.12`; from `pc3`, ping `192.168.10.11` and `192.168.10.12` using `ping -c 2`.
6. Confirm that neither `r1` nor `r2` has a default route.
7. Run `kathara lclean` when validation is complete.

Do not create the lab while responding to this prompt; this document is the implementation specification for the subsequent creation step.
