# Dual-stack static-routing star

`r0` is the central router. It connects by separate IPv4/IPv6 point-to-point links to `r1`, `r2`, and `r3`. Each edge router connects to a two-client LAN; `r0` connects to the LAN containing `main_server`.

All IPv4 and IPv6 addresses, forwarding settings, and static routes are installed by each machine's startup file. The edge routers use a static default route in both families. `r0` has explicit static routes to all three edge LANs in both families.

After starting the lab, each client can verify reachability with:

```sh
ping -c 3 10.0.10.10
ping6 -c 3 2001:db8:10::10
```
