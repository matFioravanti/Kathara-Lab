# Three-Router Static-Routing Lab

This Kathara lab demonstrates IPv4 static routing across three routers in a
linear topology. Each router serves a LAN containing five PCs. Router `r2` has
the maximum topology degree of 3, and all fifteen PCs are intended to reach one
another without a dynamic-routing protocol.

## Topology

```text
pc1_1..pc1_5            pc2_1..pc2_5            pc3_1..pc3_5
      |                        |                        |
     LAN1                     LAN2                     LAN3
      |                        |                        |
     r1----------R1_R2--------r2--------R2_R3---------r3
```

## Addressing

| Segment | Network | Router address(es) | PCs |
|---|---|---|---|
| `LAN1` | `10.1.1.0/24` | `r1: 10.1.1.1` | `10.1.1.11`–`10.1.1.15` |
| `LAN2` | `10.2.2.0/24` | `r2: 10.2.2.1` | `10.2.2.11`–`10.2.2.15` |
| `LAN3` | `10.3.3.0/24` | `r3: 10.3.3.1` | `10.3.3.11`–`10.3.3.15` |
| `R1_R2` | `10.0.12.0/30` | `r1: 10.0.12.1`, `r2: 10.0.12.2` | — |
| `R2_R3` | `10.0.23.0/30` | `r2: 10.0.23.1`, `r3: 10.0.23.2` | — |

Each PC uses the `.1` address on its local LAN as its default gateway. The
routers contain explicit routes for the two remote LANs and have IPv4
forwarding enabled.

## Start and inspect

From this directory:

```sh
kathara lstart
kathara linfo
```

Representative checks:

```sh
kathara exec pc1_1 -- ping -c 2 10.2.2.11
kathara exec pc1_1 -- ping -c 2 10.3.3.11
kathara exec pc3_1 -- traceroute 10.1.1.11
```

Inspect addresses and routes on a device:

```sh
kathara exec r2 -- ip addr show
kathara exec r2 -- ip route show
```

Stop and remove the running lab:

```sh
kathara lclean
```
