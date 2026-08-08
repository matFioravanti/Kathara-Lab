# Five-router IPv4 static-routing lab

Start the lab from this directory with `kathara lstart`. The topology contains five router LANs and these router links: R1--R2, R1--R3, R2--R4, R3--R4, and R4--R5.

Each LAN is `10.N.N.0/24` for router `RN`; its router address is `.1`, and its PCs are `.10` and `.11`. Transit links use `10.255.12.0/30`, `10.255.13.0/30`, `10.255.24.0/30`, `10.255.34.0/30`, and `10.255.45.0/30`.

Router startup files enable IPv4 forwarding and install a distinct static route for every non-directly-connected LAN and transit subnet. No router installs a default route. PCs use their directly attached router as their default gateway.
