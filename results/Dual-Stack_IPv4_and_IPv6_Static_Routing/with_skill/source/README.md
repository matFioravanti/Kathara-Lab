# Dual-stack static routing

This lab connects two IPv4/IPv6 LANs through routers `r1` and `r2`.  Every interface is configured statically; `r1` and `r2` use separate IPv4 and IPv6 static routes across the `transit` link. No dynamic routing protocol or address autoconfiguration is used.

## Topology and addressing

| Segment | IPv4 network | IPv6 prefix | Devices |
| --- | --- | --- | --- |
| `lan1` | 192.0.2.0/24 | 2001:db8:1::/64 | r1 (192.0.2.1, 2001:db8:1::1), pc1 (.11, ::11), pc2 (.12, ::12) |
| `transit` | 198.51.100.0/30 | 2001:db8:ff::/64 | r1 (.1, ::1), r2 (.2, ::2) |
| `lan2` | 203.0.113.0/24 | 2001:db8:2::/64 | r2 (203.0.113.1, 2001:db8:2::1), pc3 (.11, ::11), pc4 (.12, ::12) |

Start the laboratory from this directory:

```sh
kathara lstart
```

Verify end-to-end reachability from `pc1`:

```sh
kathara exec pc1 -- ping -c 2 203.0.113.11
kathara exec pc1 -- ping -6 -c 2 2001:db8:2::11
```
