# Five-router explicit IPv4 static-routing lab

## Topology

```
PC1A PC1B -- R1 -- R2 -- R4 -- R5 -- PC5A PC5B
                \         /
                 R3 ------
```

Each router has a two-PC LAN.  Router interfaces use the following addresses:

| Segment | IPv4 network | Router addresses |
|---|---|---|
| R1 LAN | 10.10.1.0/24 | R1 10.10.1.1 |
| R2 LAN | 10.10.2.0/24 | R2 10.10.2.1 |
| R3 LAN | 10.10.3.0/24 | R3 10.10.3.1 |
| R4 LAN | 10.10.4.0/24 | R4 10.10.4.1 |
| R5 LAN | 10.10.5.0/24 | R5 10.10.5.1 |
| R1--R2 | 10.255.12.0/30 | R1 10.255.12.1, R2 10.255.12.2 |
| R1--R3 | 10.255.13.0/30 | R1 10.255.13.1, R3 10.255.13.2 |
| R2--R4 | 10.255.24.0/30 | R2 10.255.24.1, R4 10.255.24.2 |
| R3--R4 | 10.255.34.0/30 | R3 10.255.34.1, R4 10.255.34.2 |
| R4--R5 | 10.255.45.0/30 | R4 10.255.45.1, R5 10.255.45.2 |

All router routes are explicit network routes. No router configuration contains a default route.

## Start

From this directory, start the laboratory with `kathara lstart`.  For example, test from PC1A with `ping -c 3 10.10.5.10`.
