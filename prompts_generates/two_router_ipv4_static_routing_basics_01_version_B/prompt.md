# Kathara Lab Implementation Prompt — Scenario 01, Version B

Using the `kathara-lab-creation` skill conventions, prepare a runnable Kathara lab named `two_router_ipv4_static_routing_basics` at:

`prompts_generates/two_router_ipv4_static_routing_basics_01_version_B/two_router_ipv4_static_routing_basics/`

## Learning goal

Demonstrate basic IPv4 static routing between two LANs. The topology has two routers connected by one point-to-point link; each router attaches to a LAN with two PCs. A host in either LAN must be able to ping both hosts in the opposite LAN. Use only manual IPv4 configuration and static routes; do not use dynamic routing protocols or IPv6.

## Canonical layout

Create one lab directory containing `lab.conf`, one `.startup` file per device, and `README.md`. Use `kathara/core:latest` for routers and PCs. Configure devices persistently through startup scripts with `ip` commands; do not rely on post-start interactive changes.

## Device, interface, and link plan

| Device | Interface | Collision domain | IPv4 address |
|---|---|---|---|
| r1 | eth0 | lan1 | 192.168.10.1/24 |
| r1 | eth1 | r1_r2 | 10.0.12.1/30 |
| r2 | eth0 | r1_r2 | 10.0.12.2/30 |
| r2 | eth1 | lan2 | 192.168.20.1/24 |
| pc1 | eth0 | lan1 | 192.168.10.11/24 |
| pc2 | eth0 | lan1 | 192.168.10.12/24 |
| pc3 | eth0 | lan2 | 192.168.20.11/24 |
| pc4 | eth0 | lan2 | 192.168.20.12/24 |

Declare `r1[0]`, `pc1[0]`, and `pc2[0]` on `lan1`; `r1[1]` and `r2[0]` on `r1_r2`; and `r2[1]`, `pc3[0]`, and `pc4[0]` on `lan2`. Keep each device's interface indexes contiguous. Set IPv6 disabled explicitly in `lab.conf`.

## Routing requirements

- `r1`: `ip route add 192.168.20.0/24 via 10.0.12.2`
- `r2`: `ip route add 192.168.10.0/24 via 10.0.12.1`
- `pc1` and `pc2`: default route via `192.168.10.1`
- `pc3` and `pc4`: default route via `192.168.20.1`

The two router routes must be explicit. Do not configure a default route on `r1` or `r2`, since each has exactly one remote LAN. Do not configure any dynamic routing daemon.

## Documentation and validation

In `README.md`, state the objective, render the topology in text, list the IPv4 plan, give the start command `kathara lstart`, and explain how to test remote connectivity.

When implementation is requested, validate in separate commands: run `kathara check`, start with `kathara lstart`, inspect status with `kathara linfo`, then inspect every device's `ip addr show` and `ip route show`. Use `ping -c 2` from `pc1` to `192.168.20.11` and `192.168.20.12`, and from `pc3` to `192.168.10.11` and `192.168.10.12`. Verify the routers have no default route, then stop the lab with `kathara lclean`.

Do not generate the lab files yet. Produce only the lab files when a later request explicitly authorizes lab creation from this specification.
