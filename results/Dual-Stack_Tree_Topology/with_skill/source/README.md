# Dual-stack tree topology

This lab models a static-routed tree: `r0` is the root router, `r1` and `r2` are child routers, and each router has one directly attached LAN with one PC. Every link and LAN uses IPv4 and IPv6. Child routers use dual-stack static default routes to `r0`; `r0` has explicit static routes to both child LANs.

## Topology and addressing

| Segment | IPv4 | IPv6 | Devices |
| --- | --- | --- | --- |
| `r0_r1` | `10.0.1.0/30` | `2001:db8:1::/64` | r0 `.1` / `::1`, r1 `.2` / `::2` |
| `r0_r2` | `10.0.2.0/30` | `2001:db8:2::/64` | r0 `.1` / `::1`, r2 `.2` / `::2` |
| `lan_root` | `192.168.10.0/24` | `2001:db8:10::/64` | r0 `.1` / `::1`, pc0 `.10` / `::10` |
| `lan_r1` | `192.168.20.0/24` | `2001:db8:20::/64` | r1 `.1` / `::1`, pc1 `.10` / `::10` |
| `lan_r2` | `192.168.30.0/24` | `2001:db8:30::/64` | r2 `.1` / `::1`, pc2 `.10` / `::10` |

## Run and verify

Start the laboratory from this directory:

```sh
kathara lstart
```

Verify end-to-end dual-stack connectivity, for example from `pc1`:

```sh
kathara exec pc1 -- ping -c 2 192.168.30.10
kathara exec pc1 -- ping -6 -c 2 2001:db8:30::10
```
