# Implementation-Ready Prompt: Three-Router Static-Routing Kathara Lab

Create a complete, repeatable Kathara networking lab from the specification below. Treat this document as the implementation specification. Do not silently change the topology, addressing plan, device names, interface assignments, or routing method.

## Objective

Build a Kathara lab containing three IPv4 routers and fifteen PCs, with exactly five PCs connected to the LAN of each router. The routers must use only manually configured static routes. Every PC must be able to reach every other PC, including PCs attached to either of the other two routers.

The topology must have a maximum degree of 3. Use a linear routed backbone:

```text
 pc1_1 ... pc1_5                 pc2_1 ... pc2_5                 pc3_1 ... pc3_5
        \ | /                           \ | /                           \ | /
       LAN1                            LAN2                            LAN3
         |                               |                               |
        r1---------------r2--------------r3
              R1_R2            R2_R3
```

Count each LAN attachment and each router-to-router attachment as one incident link for the router. Therefore:

- `r1` has degree 2: `LAN1` and `R1_R2`.
- `r2` has degree 3: `LAN2`, `R1_R2`, and `R2_R3`.
- `r3` has degree 2: `LAN3` and `R2_R3`.
- The maximum router degree is exactly 3.

## Explicit assumptions

- Target path: `./three-router-static-routing-15pcs`
- Lab folder name: `three-router-static-routing-15pcs`
- Address family: IPv4 only.
- Runtime image for every device: `kathara/core:latest`.
- The lab is an instructional scenario, so include a concise `README.md`.
- LANs are shared Kathara collision domains; no separate switch containers are required.
- Router-to-router links use distinct point-to-point collision domains.
- PCs use a static default route through their local router.
- Routers use explicit static routes and must not run RIP, OSPF, IS-IS, BGP, or any other dynamic-routing protocol.
- NAT, DHCP, bridging, and application services are outside the scope of the lab.
- All intended configuration must be persisted in `lab.conf` and startup files; do not rely on interactive changes.

## Devices and roles

Create these 18 devices:

| Device(s) | Quantity | Role |
|---|---:|---|
| `r1`, `r2`, `r3` | 3 | IPv4 routers with forwarding enabled |
| `pc1_1` through `pc1_5` | 5 | End hosts on `LAN1`, using `r1` as gateway |
| `pc2_1` through `pc2_5` | 5 | End hosts on `LAN2`, using `r2` as gateway |
| `pc3_1` through `pc3_5` | 5 | End hosts on `LAN3`, using `r3` as gateway |

Use exactly these device names so that startup filenames and validation commands are deterministic.

## Collision domains and interface mapping

Declare the following collision domains in `lab.conf`. Interface numbering must be contiguous from `eth0`.

| Device | Interface | Collision domain | Purpose |
|---|---|---|---|
| `r1` | `eth0` | `LAN1` | Router 1 local LAN |
| `r1` | `eth1` | `R1_R2` | Link from Router 1 to Router 2 |
| `r2` | `eth0` | `LAN2` | Router 2 local LAN |
| `r2` | `eth1` | `R1_R2` | Link from Router 2 to Router 1 |
| `r2` | `eth2` | `R2_R3` | Link from Router 2 to Router 3 |
| `r3` | `eth0` | `LAN3` | Router 3 local LAN |
| `r3` | `eth1` | `R2_R3` | Link from Router 3 to Router 2 |
| `pc1_1`–`pc1_5` | `eth0` | `LAN1` | Router 1 end-host LAN |
| `pc2_1`–`pc2_5` | `eth0` | `LAN2` | Router 2 end-host LAN |
| `pc3_1`–`pc3_5` | `eth0` | `LAN3` | Router 3 end-host LAN |

Set `image="kathara/core:latest"` for all devices. Disable IPv6 explicitly if supported by the selected `lab.conf` syntax, because this scenario tests IPv4 only. Do not assign MAC addresses unless Kathara requires them; if assigned, they must be deterministic and unique.

## IPv4 addressing plan

Use the following subnets without modification:

| Network | Prefix | Use |
|---|---|---|
| `10.1.1.0/24` | `/24` | `LAN1` |
| `10.2.2.0/24` | `/24` | `LAN2` |
| `10.3.3.0/24` | `/24` | `LAN3` |
| `10.0.12.0/30` | `/30` | `R1_R2` |
| `10.0.23.0/30` | `/30` | `R2_R3` |

Assign router addresses as follows:

| Router | Interface | Address |
|---|---|---|
| `r1` | `eth0` | `10.1.1.1/24` |
| `r1` | `eth1` | `10.0.12.1/30` |
| `r2` | `eth0` | `10.2.2.1/24` |
| `r2` | `eth1` | `10.0.12.2/30` |
| `r2` | `eth2` | `10.0.23.1/30` |
| `r3` | `eth0` | `10.3.3.1/24` |
| `r3` | `eth1` | `10.0.23.2/30` |

Assign PC addresses as follows:

| PC | Address | Default gateway |
|---|---|---|
| `pc1_1` | `10.1.1.11/24` | `10.1.1.1` |
| `pc1_2` | `10.1.1.12/24` | `10.1.1.1` |
| `pc1_3` | `10.1.1.13/24` | `10.1.1.1` |
| `pc1_4` | `10.1.1.14/24` | `10.1.1.1` |
| `pc1_5` | `10.1.1.15/24` | `10.1.1.1` |
| `pc2_1` | `10.2.2.11/24` | `10.2.2.1` |
| `pc2_2` | `10.2.2.12/24` | `10.2.2.1` |
| `pc2_3` | `10.2.2.13/24` | `10.2.2.1` |
| `pc2_4` | `10.2.2.14/24` | `10.2.2.1` |
| `pc2_5` | `10.2.2.15/24` | `10.2.2.1` |
| `pc3_1` | `10.3.3.11/24` | `10.3.3.1` |
| `pc3_2` | `10.3.3.12/24` | `10.3.3.1` |
| `pc3_3` | `10.3.3.13/24` | `10.3.3.1` |
| `pc3_4` | `10.3.3.14/24` | `10.3.3.1` |
| `pc3_5` | `10.3.3.15/24` | `10.3.3.1` |

## Static routing plan

Enable IPv4 forwarding on every router with:

```sh
sysctl -w net.ipv4.ip_forward=1
```

Configure the following routes with `ip route replace` so startup scripts remain idempotent:

### Router `r1`

```sh
ip route replace 10.2.2.0/24 via 10.0.12.2 dev eth1
ip route replace 10.3.3.0/24 via 10.0.12.2 dev eth1
```

### Router `r2`

```sh
ip route replace 10.1.1.0/24 via 10.0.12.1 dev eth1
ip route replace 10.3.3.0/24 via 10.0.23.2 dev eth2
```

### Router `r3`

```sh
ip route replace 10.1.1.0/24 via 10.0.23.1 dev eth1
ip route replace 10.2.2.0/24 via 10.0.23.1 dev eth1
```

Each PC must have one default route:

```sh
ip route replace default via <local-router-LAN-address> dev eth0
```

Do not add static routes for directly connected networks. Do not configure a default route on the routers. Do not install any dynamic-routing daemon.

## Required files to generate during the later implementation stage

Create only the following scenario files unless an implementation requirement makes an additional file essential:

```text
three-router-static-routing-15pcs/
├── lab.conf
├── README.md
├── r1.startup
├── r2.startup
├── r3.startup
├── pc1_1.startup
├── pc1_2.startup
├── pc1_3.startup
├── pc1_4.startup
├── pc1_5.startup
├── pc2_1.startup
├── pc2_2.startup
├── pc2_3.startup
├── pc2_4.startup
├── pc2_5.startup
├── pc3_1.startup
├── pc3_2.startup
├── pc3_3.startup
├── pc3_4.startup
└── pc3_5.startup
```

Requirements for those files:

- `lab.conf` must declare all devices, interfaces, collision domains, and images.
- Every device must have a matching `.startup` file.
- Startup files must use `ip address replace` or an equivalently idempotent `ip` command for addresses.
- Do not run `ip link set up`; Kathara interfaces are already up at boot.
- Router startup files must configure addresses, enable IPv4 forwarding, and install their static routes.
- PC startup files must configure their address and default route.
- `README.md` must state the objective, topology, address plan, start command (`kathara lstart`), cleanup command (`kathara lclean`), and representative connectivity checks.
- Do not create per-device root filesystem directories, `shared/`, or `images/` unless later explicitly requested.

## Validation requirements for the later validation stage

Do not validate until the user separately asks for validation. When requested, run each command independently, inspect its result, and fix persistent lab files before continuing.

1. Run `kathara check`.
2. From the lab directory, run `kathara lstart`.
3. Run `kathara linfo` and confirm all 18 devices are running with the expected interfaces.
4. On every device, inspect `ip addr show`.
5. On every device, inspect `ip route show`.
6. On each router, verify `sysctl net.ipv4.ip_forward` returns `1`.
7. Verify each PC can ping its local gateway using two packets.
8. Verify both router-to-router links in both directions.
9. Verify representative cross-LAN reachability:
   - `pc1_1` to `10.2.2.11`
   - `pc1_1` to `10.3.3.11`
   - `pc2_1` to `10.1.1.11`
   - `pc2_1` to `10.3.3.11`
   - `pc3_1` to `10.1.1.11`
   - `pc3_1` to `10.2.2.11`
10. Run a complete PC-to-PC ping matrix: from each of the 15 PCs, ping the IP address of each of the other 14 PCs with `ping -c 2`. All 210 directed tests must succeed with zero packet loss.
11. Use `traceroute` for at least one destination on each remote LAN and confirm the path follows the linear topology. In particular, traffic between `LAN1` and `LAN3` must traverse `r1`, `r2`, and `r3`.
12. Run `kathara lclean`, start the lab again, and repeat `kathara linfo` to confirm that all configuration is persistent and restart-safe.
13. Finish with `kathara lclean` unless the user asks to leave the lab running.

## Acceptance criteria

The implementation is complete only when:

- Exactly 3 routers and 15 PCs are declared.
- Exactly 5 PCs are attached to each router LAN.
- The maximum router degree is 3, attained by `r2`.
- Every address and collision domain matches this prompt.
- IPv4 forwarding is enabled on all routers.
- Routing between LANs is provided exclusively by the specified static routes.
- Every PC can reach all 14 other PCs.
- The lab survives a clean stop and restart without interactive reconfiguration.
- No lab creation or validation occurs before the user explicitly requests the corresponding later stage.
