# Five-router explicit IPv4 routing

This lab has five routers and five LANs. Each LAN contains two PCs. Every router uses only explicitly configured, subnet-specific IPv4 static routes for non-connected networks; no router has a default route.

## Addressing

| Segment | Network | Router address(es) |
| --- | --- | --- |
| LAN 1 | `10.1.1.0/24` | R1 `10.1.1.1` |
| LAN 2 | `10.2.2.0/24` | R2 `10.2.2.1` |
| LAN 3 | `10.3.3.0/24` | R3 `10.3.3.1` |
| LAN 4 | `10.4.4.0/24` | R4 `10.4.4.1` |
| LAN 5 | `10.5.5.0/24` | R5 `10.5.5.1` |
| R1-R2 | `10.255.12.0/30` | R1 `10.255.12.1`, R2 `10.255.12.2` |
| R1-R3 | `10.255.13.0/30` | R1 `10.255.13.1`, R3 `10.255.13.2` |
| R2-R4 | `10.255.24.0/30` | R2 `10.255.24.1`, R4 `10.255.24.2` |
| R3-R4 | `10.255.34.0/30` | R3 `10.255.34.1`, R4 `10.255.34.2` |
| R4-R5 | `10.255.45.0/30` | R4 `10.255.45.1`, R5 `10.255.45.2` |

Each LAN's PCs use `.10` and `.11`; their local router (`.1`) is their default gateway.

## Run and check

Start the laboratory with:

```sh
kathara lstart
```

For a quick end-to-end check, from `pc1a` ping `pc5b`:

```sh
kathara exec pc1a -- ping -c 2 10.5.5.11
```
