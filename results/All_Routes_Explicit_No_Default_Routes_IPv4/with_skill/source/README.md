# Five-router explicit IPv4 static routing

This laboratory has five routers and five LANs. R1 connects to R2 and R3; R2 and R3 each connect to R4; and R4 connects to R5. Each LAN contains two PCs. Every router has a specific static route for every subnet that is not directly connected; router default routes are intentionally absent.

Start the laboratory from this directory:

```sh
kathara lstart
```

For a quick end-to-end check, run `ping -c 2 10.5.0.12` from `pc1a`. The ten PCs use their respective local router as the default gateway.

## Addressing

| Segment | IPv4 subnet | Router addresses |
| --- | --- | --- |
| LAN 1 | 10.1.0.0/24 | R1: 10.1.0.1 |
| LAN 2 | 10.2.0.0/24 | R2: 10.2.0.1 |
| LAN 3 | 10.3.0.0/24 | R3: 10.3.0.1 |
| LAN 4 | 10.4.0.0/24 | R4: 10.4.0.1 |
| LAN 5 | 10.5.0.0/24 | R5: 10.5.0.1 |
| R1-R2 | 10.255.12.0/30 | R1: .1, R2: .2 |
| R1-R3 | 10.255.13.0/30 | R1: .1, R3: .2 |
| R2-R4 | 10.255.24.0/30 | R2: .1, R4: .2 |
| R3-R4 | 10.255.34.0/30 | R3: .1, R4: .2 |
| R4-R5 | 10.255.45.0/30 | R4: .1, R5: .2 |
