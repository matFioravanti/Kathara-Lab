# Static routing and hierarchical DNS

## Objective

This teaching lab demonstrates IPv4 forwarding through five statically routed
routers and private hierarchical DNS delegation. A client resolves
`kathara.org` by walking a private root, `org.`, and `kathara.org.` hierarchy,
then reaches an Apache server by name.

The scenario contains exactly five routers, three network DNS servers, one
client, and one web server. It uses no NAT, dynamic routing, public DNS, package
downloads, or `/etc/hosts` entry for `kathara.org`.

## Images and assumptions

- Routers, client, and web server: `kathara/base`
- DNS servers: `kathara/bind:latest`
- IPv4 only; IPv6 is disabled in `lab.conf`.
- The images must already be locally available or pullable before the lab is
  started.
- Normal lab startup requires no Internet access.
- `kathara/base` supplies the common network tools and Apache.
- `kathara/bind:latest` supplies BIND 9 on the three DNS nodes.

## Topology

```text
                      ROOT_LAN
                    dnsroot
                       |
CLIENT_LAN            r2-------------r5-----------server
client---r1           /                \           SERVER_LAN
          |\         /                  \
          | \-------r3                  |
          |       ORG_LAN               |
          |       dnsorg                |
          |                             |
          \----------r4-----------------/
                  LOCAL_LAN
                  dnslocal

Router edges:
r1-r2, r1-r3, r1-r4, r2-r5, r3-r5, r4-r5
```

### Router degree

Only router-to-router neighbors count toward degree.

| Router | Router neighbors | Degree |
|---|---|---:|
| `r1` | `r2`, `r3`, `r4` | 3 |
| `r2` | `r1`, `r5` | 2 |
| `r3` | `r1`, `r5` | 2 |
| `r4` | `r1`, `r5` | 2 |
| `r5` | `r2`, `r3`, `r4` | 3 |

The maximum router degree is exactly **3**.

## Interfaces and addressing

| Device | Interface | Collision domain | Address/prefix | Default gateway |
|---|---|---|---|---|
| `r1` | `eth0` | `R1R2` | `10.0.12.1/30` | — |
| `r1` | `eth1` | `R1R3` | `10.0.13.1/30` | — |
| `r1` | `eth2` | `R1R4` | `10.0.14.1/30` | — |
| `r1` | `eth3` | `CLIENT_LAN` | `10.10.1.1/24` | — |
| `r2` | `eth0` | `R1R2` | `10.0.12.2/30` | — |
| `r2` | `eth1` | `R2R5` | `10.0.25.1/30` | — |
| `r2` | `eth2` | `ROOT_LAN` | `10.10.2.1/24` | — |
| `r3` | `eth0` | `R1R3` | `10.0.13.2/30` | — |
| `r3` | `eth1` | `R3R5` | `10.0.35.1/30` | — |
| `r3` | `eth2` | `ORG_LAN` | `10.10.3.1/24` | — |
| `r4` | `eth0` | `R1R4` | `10.0.14.2/30` | — |
| `r4` | `eth1` | `R4R5` | `10.0.45.1/30` | — |
| `r4` | `eth2` | `LOCAL_LAN` | `10.10.4.1/24` | — |
| `r5` | `eth0` | `R2R5` | `10.0.25.2/30` | — |
| `r5` | `eth1` | `R3R5` | `10.0.35.2/30` | — |
| `r5` | `eth2` | `R4R5` | `10.0.45.2/30` | — |
| `r5` | `eth3` | `SERVER_LAN` | `10.10.5.1/24` | — |
| `client` | `eth0` | `CLIENT_LAN` | `10.10.1.10/24` | `10.10.1.1` |
| `dnsroot` | `eth0` | `ROOT_LAN` | `10.10.2.10/24` | `10.10.2.1` |
| `dnsorg` | `eth0` | `ORG_LAN` | `10.10.3.10/24` | `10.10.3.1` |
| `dnslocal` | `eth0` | `LOCAL_LAN` | `10.10.4.10/24` | `10.10.4.1` |
| `server` | `eth0` | `SERVER_LAN` | `10.10.5.10/24` | `10.10.5.1` |

The six router links use distinct `/30` networks. The five end-system LANs use
distinct `/24` networks. None overlap.

## Static routes

Every router enables `net.ipv4.ip_forward=1`. Connected routes are installed by
interface addressing; these are all routes to non-connected subnets.

### `r1`

| Destination | Next hop | Interface |
|---|---|---|
| `10.0.25.0/30` | `10.0.12.2` | `eth0` |
| `10.0.35.0/30` | `10.0.13.2` | `eth1` |
| `10.0.45.0/30` | `10.0.14.2` | `eth2` |
| `10.10.2.0/24` | `10.0.12.2` | `eth0` |
| `10.10.3.0/24` | `10.0.13.2` | `eth1` |
| `10.10.4.0/24` | `10.0.14.2` | `eth2` |
| `10.10.5.0/24` | `10.0.12.2` | `eth0` |

### `r2`

| Destination | Next hop | Interface |
|---|---|---|
| `10.0.13.0/30` | `10.0.12.1` | `eth0` |
| `10.0.14.0/30` | `10.0.12.1` | `eth0` |
| `10.0.35.0/30` | `10.0.25.2` | `eth1` |
| `10.0.45.0/30` | `10.0.25.2` | `eth1` |
| `10.10.1.0/24` | `10.0.12.1` | `eth0` |
| `10.10.3.0/24` | `10.0.12.1` | `eth0` |
| `10.10.4.0/24` | `10.0.12.1` | `eth0` |
| `10.10.5.0/24` | `10.0.25.2` | `eth1` |

### `r3`

| Destination | Next hop | Interface |
|---|---|---|
| `10.0.12.0/30` | `10.0.13.1` | `eth0` |
| `10.0.14.0/30` | `10.0.13.1` | `eth0` |
| `10.0.25.0/30` | `10.0.35.2` | `eth1` |
| `10.0.45.0/30` | `10.0.35.2` | `eth1` |
| `10.10.1.0/24` | `10.0.13.1` | `eth0` |
| `10.10.2.0/24` | `10.0.13.1` | `eth0` |
| `10.10.4.0/24` | `10.0.13.1` | `eth0` |
| `10.10.5.0/24` | `10.0.35.2` | `eth1` |

### `r4`

| Destination | Next hop | Interface |
|---|---|---|
| `10.0.12.0/30` | `10.0.14.1` | `eth0` |
| `10.0.13.0/30` | `10.0.14.1` | `eth0` |
| `10.0.25.0/30` | `10.0.45.2` | `eth1` |
| `10.0.35.0/30` | `10.0.45.2` | `eth1` |
| `10.10.1.0/24` | `10.0.14.1` | `eth0` |
| `10.10.2.0/24` | `10.0.14.1` | `eth0` |
| `10.10.3.0/24` | `10.0.14.1` | `eth0` |
| `10.10.5.0/24` | `10.0.45.2` | `eth1` |

### `r5`

| Destination | Next hop | Interface |
|---|---|---|
| `10.0.12.0/30` | `10.0.25.1` | `eth0` |
| `10.0.13.0/30` | `10.0.35.1` | `eth1` |
| `10.0.14.0/30` | `10.0.45.1` | `eth2` |
| `10.10.1.0/24` | `10.0.25.1` | `eth0` |
| `10.10.2.0/24` | `10.0.25.1` | `eth0` |
| `10.10.3.0/24` | `10.0.35.1` | `eth1` |
| `10.10.4.0/24` | `10.0.45.1` | `eth2` |

No RIP, OSPF, IS-IS, BGP, Babel, NAT, or other dynamic forwarding mechanism
is configured.

## DNS hierarchy

```text
client (/etc/resolv.conf -> 10.10.2.10)
  |
  +-- dnsroot, recursive resolver and authoritative for .
        a.root.lab. = 10.10.2.10
        delegates org. to ns.org.
  |
  +-- dnsorg, authoritative for org.
        ns.org. = 10.10.3.10
        delegates kathara.org. to ns.kathara.org.
  |
  +-- dnslocal, authoritative for kathara.org.
        ns.kathara.org. = 10.10.4.10
        kathara.org. = 10.10.5.10
```

`dnsroot` supplies recursion to the client and glue for `ns.org.`. `dnsorg` supplies glue for
`ns.kathara.org.` and intentionally has no application-server record.
`dnslocal` supplies the authoritative apex `A` record.

Like the PCs in the reference DNS lab, the client does not run BIND.
Its `/etc/resolv.conf` points to `dnsroot` at `10.10.2.10`. `dnsroot` accepts
recursive requests from `CLIENT_LAN`, starts from its private root zone, and
follows the delegations to `dnsorg` and `dnslocal`. DNSSEC validation is
disabled because this isolated hierarchy is unsigned.

## Web service

Apache on `server` serves a deterministic page on TCP port 80. It contains:

```text
kathara.org
Static routing and hierarchical DNS are working.
```

## Starting and inspecting the lab

From this directory:

```sh
kathara check
kathara lstart
kathara linfo
```

Connect interactively:

```sh
kathara connect client
```

Inspect a node non-interactively:

```sh
kathara exec r1 -- ip addr show
kathara exec r1 -- ip route show
```

## Validation procedure

Run validation commands separately and examine each result before continuing.

### Direct router links

```sh
kathara exec r1 -- ping -c 2 10.0.12.2
kathara exec r1 -- ping -c 2 10.0.13.2
kathara exec r1 -- ping -c 2 10.0.14.2
kathara exec r2 -- ping -c 2 10.0.25.2
kathara exec r3 -- ping -c 2 10.0.35.2
kathara exec r4 -- ping -c 2 10.0.45.2
```

Expected: every command receives two replies.

### End-to-end addressing

```sh
kathara exec client -- ip addr show
kathara exec client -- ip route show
kathara exec client -- ping -c 2 10.10.1.1
kathara exec client -- ping -c 2 10.10.2.10
kathara exec client -- ping -c 2 10.10.3.10
kathara exec client -- ping -c 2 10.10.4.10
kathara exec client -- ping -c 2 10.10.5.10
```

Expected: the client has `10.10.1.10/24`, its default route uses
`10.10.1.1`, and every ping receives two replies.

### Services

```sh
kathara exec dnsroot -- systemctl status bind9
kathara exec dnsorg -- systemctl status bind9
kathara exec dnslocal -- systemctl status bind9
kathara exec server -- systemctl status apache2
kathara exec dnsroot -- ss -lntup
kathara exec dnsorg -- ss -lntup
kathara exec dnslocal -- ss -lntup
kathara exec server -- ss -lntup
```

Expected: each unit is active; the authorities listen on TCP and UDP port 53
at their lab addresses; Apache listens on TCP port 80.

### DNS delegations

```sh
kathara exec client -- dig @10.10.2.10 org. NS +norecurse
kathara exec client -- dig @10.10.3.10 kathara.org. NS +norecurse
kathara exec client -- dig @10.10.4.10 kathara.org. A +norecurse
kathara exec client -- dig kathara.org. A
```

Expected:

1. The root response delegates `org.` to `ns.org.` and supplies
   `10.10.3.10` as glue.
2. The `org.` response delegates `kathara.org.` to `ns.kathara.org.` and
   supplies `10.10.4.10` as glue.
3. The local authoritative response has the `AA` flag and returns
   `10.10.5.10`.
4. The client's configured resolver, `dnsroot`, resolves the full hierarchy
   and returns `10.10.5.10`.

### Hostname-based application test

```sh
kathara exec client -- ping -c 2 kathara.org
kathara exec client -- curl --fail --show-error http://kathara.org/
```

Expected: the name resolves to `10.10.5.10`; ping succeeds; curl returns the
deterministic HTML page.

If a check fails, diagnose one failure at a time with commands such as:

```sh
kathara exec client -- traceroute 10.10.5.10
kathara exec client -- tcpdump -ni eth0 port 53
kathara exec dnsroot -- cat /var/log/syslog
```

Persist corrections in lab files rather than making interactive-only changes.

## Cleanup and restart check

```sh
kathara lclean
kathara lstart
kathara linfo
kathara lclean
```

The second start should reproduce the same addresses, routes, DNS data, and
web content.
