# Five-router explicit IPv4 routing lab

This lab connects five router LANs in a redundant R1--R2--R4--R5 and R1--R3--R4 topology. Each LAN contains its router plus two PCs. IPv4 forwarding and all router routes are configured in startup files; routers use only explicit routes and have no default route.

## Run

From this directory, start the laboratory with:

```sh
kathara lstart
```

## Addressing

| LAN | Router | PCs |
| --- | --- | --- |
| 10.1.1.0/24 | R1: 10.1.1.1 | pc1a: 10.1.1.11, pc1b: 10.1.1.12 |
| 10.1.2.0/24 | R2: 10.1.2.1 | pc2a: 10.1.2.11, pc2b: 10.1.2.12 |
| 10.1.3.0/24 | R3: 10.1.3.1 | pc3a: 10.1.3.11, pc3b: 10.1.3.12 |
| 10.1.4.0/24 | R4: 10.1.4.1 | pc4a: 10.1.4.11, pc4b: 10.1.4.12 |
| 10.1.5.0/24 | R5: 10.1.5.1 | pc5a: 10.1.5.11, pc5b: 10.1.5.12 |

The router transit networks are 10.255.12.0/30 (R1--R2), 10.255.13.0/30 (R1--R3), 10.255.24.0/30 (R2--R4), 10.255.34.0/30 (R3--R4), and 10.255.45.0/30 (R4--R5).

## Quick check

After startup, verify end-to-end connectivity, for example:

```sh
kathara exec pc1a -- ping -c 2 10.1.5.12
kathara exec pc5b -- ping -c 2 10.1.2.11
```
