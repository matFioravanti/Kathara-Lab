# Five-router IPv4 static-routing lab

Start the lab from this directory with `kathara lstart`.

The routers form two paths between R1 and R4: R1--R2--R4 and R1--R3--R4. R4 connects to R5. Each router has a two-host LAN.

| LAN | Router | Hosts |
| --- | --- | --- |
| 10.1.1.0/24 | R1: 10.1.1.1 | pc1a: 10.1.1.10, pc1b: 10.1.1.11 |
| 10.2.2.0/24 | R2: 10.2.2.1 | pc2a: 10.2.2.10, pc2b: 10.2.2.11 |
| 10.3.3.0/24 | R3: 10.3.3.1 | pc3a: 10.3.3.10, pc3b: 10.3.3.11 |
| 10.4.4.0/24 | R4: 10.4.4.1 | pc4a: 10.4.4.10, pc4b: 10.4.4.11 |
| 10.5.5.0/24 | R5: 10.5.5.1 | pc5a: 10.5.5.10, pc5b: 10.5.5.11 |

Transit links use /30 networks: R1--R2 `10.255.12.0/30`, R1--R3 `10.255.13.0/30`, R2--R4 `10.255.24.0/30`, R3--R4 `10.255.34.0/30`, and R4--R5 `10.255.45.0/30`.

Each router startup file enables IPv4 forwarding, removes any default route, and installs a specific static route to every non-directly-connected LAN and transit subnet. PCs use their local router as their default gateway.
