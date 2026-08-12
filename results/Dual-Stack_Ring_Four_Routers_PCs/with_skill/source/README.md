# Dual-stack static-routing ring

Four routers form a ring. Each router connects a dedicated dual-stack LAN containing two PCs. IPv4 and IPv6 routing is exclusively static: no default route is configured anywhere.

Start the laboratory with `kathara lstart`. For a quick end-to-end check, from `pc1a` run `ping -c 2 10.1.4.12` and `ping -6 -c 2 fd00:1:4::12`.

Inter-router links are `ring12`, `ring23`, `ring34`, and `ring41`; each router has exactly two router-to-router interfaces.
