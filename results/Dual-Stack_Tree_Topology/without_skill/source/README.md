# Dual-stack tree topology

The lab contains three routers (`root`, `child1`, and `child2`) and one PC on each router LAN.  All interface addresses and all static routes are set when the containers start.

| Segment | IPv4 network | IPv6 network |
|---|---|---|
| root--child1 | `10.0.1.0/30` | `fd00:1::/64` |
| root--child2 | `10.0.2.0/30` | `fd00:2::/64` |
| root LAN | `192.168.10.0/24` | `fd00:10::/64` |
| child1 LAN | `192.168.20.0/24` | `fd00:20::/64` |
| child2 LAN | `192.168.30.0/24` | `fd00:30::/64` |

After starting the lab, verify end-to-end dual-stack reachability from any PC, for example:

```sh
kathara exec pc1 -- ping -c 3 192.168.30.10
kathara exec pc1 -- ping -6 -c 3 fd00:30::10
```

The root has explicit IPv4 and IPv6 static routes to both child LANs. Each child router has IPv4 and IPv6 default routes through the root.
