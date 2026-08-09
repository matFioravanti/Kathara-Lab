# Five-router explicit IPv4 routing lab

The lab implements this topology: R1--R2--R4--R5, with a second path R1--R3--R4. Each router has a two-PC LAN. All addressing is IPv4-only.

| LAN | Router address | PCs |
| --- | --- | --- |
| `10.1.1.0/24` | R1: `10.1.1.1` | `10.1.1.11`, `10.1.1.12` |
| `10.2.2.0/24` | R2: `10.2.2.1` | `10.2.2.11`, `10.2.2.12` |
| `10.3.3.0/24` | R3: `10.3.3.1` | `10.3.3.11`, `10.3.3.12` |
| `10.4.4.0/24` | R4: `10.4.4.1` | `10.4.4.11`, `10.4.4.12` |
| `10.5.5.0/24` | R5: `10.5.5.1` | `10.5.5.11`, `10.5.5.12` |

Transit networks are `10.12.0.0/30` (R1-R2), `10.13.0.0/30` (R1-R3), `10.24.0.0/30` (R2-R4), `10.34.0.0/30` (R3-R4), and `10.45.0.0/30` (R4-R5). Every router startup file enables IPv4 forwarding and installs a specific route to each non-connected LAN and transit subnet. No default routes are configured.

Start the lab from this directory with `kathara lstart`. For example, `kathara exec pc1a -- ping -c 3 10.5.5.12` tests an end-to-end path.
