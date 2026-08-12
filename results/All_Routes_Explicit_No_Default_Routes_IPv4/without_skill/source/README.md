# Five-router IPv4 static-routing lab

The lab contains routers `R1` through `R5` and two PCs on each router LAN. Router links are `10.0.12.0/30`, `10.0.13.0/30`, `10.0.24.0/30`, `10.0.34.0/30`, and `10.0.45.0/30`. LANs use `192.168.1.0/24` through `192.168.5.0/24`.

Each router startup file enables IPv4 forwarding and installs a specific route for every subnet that is not directly connected. No router has a default route. PCs use their local router as their default gateway.

Start the lab from this directory with `kathara lstart`. For example, verify end-to-end connectivity with `kathara exec PC1A -- ping -c 3 192.168.5.11`.
