# Dual-stack line topology

This lab has three statically routed routers in a line. Each router provides one LAN containing three dual-stack PCs. IPv4 and IPv6 are configured on every LAN and every inter-router link. Edge routers use static default routes, while the middle router has explicit routes to both edge LANs.

Start the lab with:

```sh
kathara lstart
```

For a quick end-to-end check, from `pc1` ping a PC on the far LAN with both protocols:

```sh
ping -c 2 10.10.3.13
ping -6 -c 2 2001:db8:10:3::13
```
