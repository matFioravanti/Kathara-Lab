# Implementation Prompt: Five-Router Static-Routing and Hierarchical-DNS Kathará Lab

Create a complete, repeatable Kathará teaching lab from the following
specification. Do not leave topology, addressing, routing, DNS, image, or
validation decisions unresolved.

## 1. Target and assumptions

- Create the scenario in a new folder named
  `static-routing-hierarchical-dns/`, relative to the directory from which the
  implementation request is executed.
- Treat that folder as the lab root.
- Use IPv4 only.
- Use `kathara/core:latest` for routers.
- Use `kathara/base:latest` for the client, the three DNS server nodes, and the
  web server because that image includes BIND 9, Apache, dnsmasq, and common
  network tools.
- Assume the audience is students; generate a clear `README.md`.
- Do not install packages during lab startup and do not require Internet
  access.
- Persist every intended configuration in lab files. Do not rely on
  interactive, ephemeral container changes.
- Use `ip` for addressing and routes.
- Kathará interfaces are already up at boot: do not add `ip link set ... up`
  commands.
- Use `systemctl` to manage BIND and Apache services, as required by the
  Kathará lab-creation workflow.

## 2. Required nodes and roles

Create exactly these ten devices:

| Device | Role |
|---|---|
| `r1` | Router and gateway for the client LAN |
| `r2` | Router and gateway for the root-DNS LAN |
| `r3` | Router and gateway for the `org`-DNS LAN |
| `r4` | Router and gateway for the local-DNS LAN |
| `r5` | Router and gateway for the application-server LAN |
| `dnsroot` | Authoritative DNS root server |
| `dnsorg` | Authoritative DNS server for `org.` |
| `dnslocal` | Authoritative DNS server for `kathara.org.` |
| `server` | HTTP server addressed by the name `kathara.org` |
| `client` | End host that resolves and reaches `kathara.org` |

There must be exactly five router devices and exactly three network DNS server
devices.

## 3. Router topology and degree constraint

Connect the five routers using exactly these six undirected links:

| Collision domain | Endpoint 1 | Endpoint 2 |
|---|---|---|
| `R1R2` | `r1` | `r2` |
| `R1R3` | `r1` | `r3` |
| `R1R4` | `r1` | `r4` |
| `R2R5` | `r2` | `r5` |
| `R3R5` | `r3` | `r5` |
| `R4R5` | `r4` | `r5` |

Do not add other router-to-router links. End-system LANs do not count as router
neighbors.

The resulting degree calculation must be included in the README:

| Router | Router neighbors | Degree |
|---|---|---:|
| `r1` | `r2`, `r3`, `r4` | 3 |
| `r2` | `r1`, `r5` | 2 |
| `r3` | `r1`, `r5` | 2 |
| `r4` | `r1`, `r5` | 2 |
| `r5` | `r2`, `r3`, `r4` | 3 |

The maximum router degree is therefore exactly 3.

## 4. End-system collision domains

Use one separate LAN for each end system:

| Collision domain | Router | End system |
|---|---|---|
| `CLIENT_LAN` | `r1` | `client` |
| `ROOT_LAN` | `r2` | `dnsroot` |
| `ORG_LAN` | `r3` | `dnsorg` |
| `LOCAL_LAN` | `r4` | `dnslocal` |
| `SERVER_LAN` | `r5` | `server` |

## 5. Interface mapping and addressing

Declare interfaces contiguously from `eth0` in `lab.conf`. Use the following
mapping and addresses exactly:

| Device | Interface | Collision domain | IPv4 address |
|---|---|---|---|
| `r1` | `eth0` | `R1R2` | `10.0.12.1/30` |
| `r1` | `eth1` | `R1R3` | `10.0.13.1/30` |
| `r1` | `eth2` | `R1R4` | `10.0.14.1/30` |
| `r1` | `eth3` | `CLIENT_LAN` | `10.10.1.1/24` |
| `r2` | `eth0` | `R1R2` | `10.0.12.2/30` |
| `r2` | `eth1` | `R2R5` | `10.0.25.1/30` |
| `r2` | `eth2` | `ROOT_LAN` | `10.10.2.1/24` |
| `r3` | `eth0` | `R1R3` | `10.0.13.2/30` |
| `r3` | `eth1` | `R3R5` | `10.0.35.1/30` |
| `r3` | `eth2` | `ORG_LAN` | `10.10.3.1/24` |
| `r4` | `eth0` | `R1R4` | `10.0.14.2/30` |
| `r4` | `eth1` | `R4R5` | `10.0.45.1/30` |
| `r4` | `eth2` | `LOCAL_LAN` | `10.10.4.1/24` |
| `r5` | `eth0` | `R2R5` | `10.0.25.2/30` |
| `r5` | `eth1` | `R3R5` | `10.0.35.2/30` |
| `r5` | `eth2` | `R4R5` | `10.0.45.2/30` |
| `r5` | `eth3` | `SERVER_LAN` | `10.10.5.1/24` |
| `client` | `eth0` | `CLIENT_LAN` | `10.10.1.10/24` |
| `dnsroot` | `eth0` | `ROOT_LAN` | `10.10.2.10/24` |
| `dnsorg` | `eth0` | `ORG_LAN` | `10.10.3.10/24` |
| `dnslocal` | `eth0` | `LOCAL_LAN` | `10.10.4.10/24` |
| `server` | `eth0` | `SERVER_LAN` | `10.10.5.10/24` |

Use these end-host default gateways:

- `client`: `10.10.1.1`
- `dnsroot`: `10.10.2.1`
- `dnsorg`: `10.10.3.1`
- `dnslocal`: `10.10.4.1`
- `server`: `10.10.5.1`

All eleven subnets must be distinct and non-overlapping. Do not configure NAT.

## 6. Static routing

Enable IPv4 forwarding on all routers. Use connected routes and explicit static
routes only. Do not install, start, or configure RIP, OSPF, IS-IS, BGP, Babel,
or another dynamic routing protocol.

Install a route on each router for every non-connected subnet, using these
deterministic next-hop rules:

### `r1`

- Reach `10.0.25.0/30`, `10.10.2.0/24`, and `10.10.5.0/24` through
  `10.0.12.2` on `eth0`.
- Reach `10.0.35.0/30` and `10.10.3.0/24` through `10.0.13.2` on `eth1`.
- Reach `10.0.45.0/30` and `10.10.4.0/24` through `10.0.14.2` on `eth2`.

### `r2`

- Reach `10.0.13.0/30`, `10.0.14.0/30`, `10.10.1.0/24`,
  `10.10.3.0/24`, and `10.10.4.0/24` through `10.0.12.1` on `eth0`.
- Reach `10.0.35.0/30`, `10.0.45.0/30`, and `10.10.5.0/24` through
  `10.0.25.2` on `eth1`.

### `r3`

- Reach `10.0.12.0/30`, `10.0.14.0/30`, `10.10.1.0/24`,
  `10.10.2.0/24`, and `10.10.4.0/24` through `10.0.13.1` on `eth0`.
- Reach `10.0.25.0/30`, `10.0.45.0/30`, and `10.10.5.0/24` through
  `10.0.35.2` on `eth1`.

### `r4`

- Reach `10.0.12.0/30`, `10.0.13.0/30`, `10.10.1.0/24`,
  `10.10.2.0/24`, and `10.10.3.0/24` through `10.0.14.1` on `eth0`.
- Reach `10.0.25.0/30`, `10.0.35.0/30`, and `10.10.5.0/24` through
  `10.0.45.2` on `eth1`.

### `r5`

- Reach `10.0.12.0/30`, `10.10.1.0/24`, and `10.10.2.0/24` through
  `10.0.25.1` on `eth0`.
- Reach `10.0.13.0/30` and `10.10.3.0/24` through `10.0.35.1` on
  `eth1`.
- Reach `10.0.14.0/30` and `10.10.4.0/24` through `10.0.45.1` on
  `eth2`.

Use idempotent route commands such as `ip route replace`.

## 7. Hierarchical DNS

Implement genuine private DNS delegation with BIND 9. All names below are
absolute DNS names where appropriate, and zone files must contain valid SOA,
NS, and glue records.

### `dnsroot`

- Be authoritative for the root zone `.`.
- Use `a.root.lab.` as the root nameserver, with address `10.10.2.10`.
- Delegate `org.` to `ns.org.`.
- Include glue `ns.org. A 10.10.3.10`.
- Disable recursion.
- Listen on TCP and UDP port 53 at `10.10.2.10`.

### `dnsorg`

- Be authoritative for `org.`.
- Use `ns.org.` as the zone nameserver, with address `10.10.3.10`.
- Delegate `kathara.org.` to `ns.kathara.org.`.
- Include glue `ns.kathara.org. A 10.10.4.10`.
- Do not contain the final application-server `A` record.
- Disable recursion.
- Listen on TCP and UDP port 53 at `10.10.3.10`.

### `dnslocal`

- Be authoritative for `kathara.org.`.
- Use `ns.kathara.org.` as the authoritative nameserver, with address
  `10.10.4.10`.
- Define the zone-apex record `kathara.org. A 10.10.5.10`.
- Optionally define `www.kathara.org. A 10.10.5.10`.
- Disable recursion.
- Listen on TCP and UDP port 53 at `10.10.4.10`.

Use a fixed, valid SOA serial such as `2026072901` and internally consistent
refresh, retry, expiry, and negative-cache values.

## 8. Client name resolution

Normal client applications must resolve `kathara.org` without `/etc/hosts`,
public DNS, or Internet access.

Run a loopback-only BIND caching resolver on `client`:

- Listen only on `127.0.0.1`.
- Permit queries and recursion only from `127.0.0.1`.
- Configure a private root-hints file containing only:
  `a.root.lab. A 10.10.2.10`.
- Disable DNSSEC validation because the private hierarchy is unsigned.
- Point `/etc/resolv.conf` only to `127.0.0.1`.

This loopback cache is a client-side resolver component, not an additional
network DNS server node. Its iterative lookup must follow:

```text
dnsroot (.) -> dnsorg (org.) -> dnslocal (kathara.org.)
```

## 9. Application server

Configure Apache on `server`:

- Listen on TCP port 80.
- Start automatically through `systemctl`.
- Serve a deterministic page at `/` containing both `kathara.org` and the
  sentence `Static routing and hierarchical DNS are working.`
- Do not fetch page content or dependencies from the Internet.

The client must successfully reach this service using
`http://kathara.org/`.

## 10. Required files

Generate at least:

```text
static-routing-hierarchical-dns/
├── lab.conf
├── README.md
├── r1.startup
├── r2.startup
├── r3.startup
├── r4.startup
├── r5.startup
├── client.startup
├── dnsroot.startup
├── dnsorg.startup
├── dnslocal.startup
├── server.startup
├── client/etc/bind/named.conf
├── client/etc/bind/db.root.lab
├── dnsroot/etc/bind/named.conf
├── dnsroot/etc/bind/db.root.lab
├── dnsorg/etc/bind/named.conf
├── dnsorg/etc/bind/db.org
├── dnslocal/etc/bind/named.conf
├── dnslocal/etc/bind/db.kathara.org
└── server/var/www/html/index.html
```

Add other files only when they are required by the chosen Debian 12 service
configuration. Every device declared in `lab.conf` must have a matching
startup file.

In `lab.conf`:

- Add `LAB_DESCRIPTION`, `LAB_VERSION`, and `LAB_AUTHOR` metadata.
- Declare all device images explicitly.
- Disable IPv6 explicitly if the selected Kathará syntax supports it.
- Keep interface indices contiguous.
- Use collision-domain labels exactly as specified above.

Startup scripts must be non-interactive and idempotent where practical.
Configure addresses before routes and routes before dependent services. Check
BIND configuration and zone syntax before starting BIND. Use `systemctl` for
BIND and Apache service management.

## 11. README requirements

Document:

- The learning objective.
- The complete node and interface table.
- An ASCII or Mermaid topology diagram.
- The router-neighbor degree calculation.
- Every static route, grouped by router.
- DNS zones, delegations, glue records, and the client resolver path.
- The selected images and the no-Internet startup assumption.
- Exact start, inspection, test, and cleanup commands.
- Expected results for all validation commands.

## 12. Validation

Do not claim success from file inspection alone. When explicitly asked to
validate the generated lab, follow the Kathará skill workflow and run each
command separately, examining the result before continuing:

1. Run `kathara check`.
2. Run `kathara lstart` from the generated lab directory.
3. Run `kathara linfo`.
4. On every node, separately run:
   - `kathara exec <device> -- ip addr show`
   - `kathara exec <device> -- ip route show`
5. Test every directly connected router link with separate two-packet pings.
6. From `client`, separately test:
   - `ping -c 2 10.10.1.1`
   - `ping -c 2 10.10.2.10`
   - `ping -c 2 10.10.3.10`
   - `ping -c 2 10.10.4.10`
   - `ping -c 2 10.10.5.10`
7. Verify the services separately:
   - `systemctl status bind9` on `client`, `dnsroot`, `dnsorg`, and
     `dnslocal`
   - `systemctl status apache2` on `server`
   - `ss -lntup` on the DNS nodes and server
8. Verify each DNS step explicitly:
   - `dig @10.10.2.10 org. NS +norecurse`
   - `dig @10.10.3.10 kathara.org. NS +norecurse`
   - `dig @10.10.4.10 kathara.org. A +norecurse`
   - `dig @127.0.0.1 kathara.org. A` on `client`
9. Verify hostname-based application access from `client`:
   - `ping -c 2 kathara.org`
   - `curl --fail --show-error http://kathara.org/`
10. Use `traceroute` and `tcpdump` for path or DNS diagnosis if a check fails.
11. Run `kathara lclean`.
12. Start the lab again with `kathara lstart`, check it with
    `kathara linfo`, and finally clean it with `kathara lclean`.

If a validation step fails, inspect the single failure, persist the correction
in the lab files, and rerun that step and all later steps. Do not use manual
interactive changes as the final fix.

## 13. Completion checks

Before presenting the generated lab, confirm:

- There are exactly five routers.
- The router graph contains exactly the six specified edges.
- No router has degree greater than 3.
- There are exactly three network DNS server nodes.
- All interface addresses are unique and all subnets are non-overlapping.
- All five routers enable IPv4 forwarding.
- Every non-connected subnet has a static route and a valid return path.
- No dynamic-routing protocol or NAT is configured.
- Root and `org.` delegation glue matches the real DNS server addresses.
- `kathara.org.` resolves to `10.10.5.10`.
- The client uses no public DNS and no target-name entry in `/etc/hosts`.
- All interface numbers, collision domains, addresses, routes, DNS records,
  documentation, and tests agree.
- The deterministic web page is available through the hostname
  `kathara.org`.

Return the generated directory tree, summarize the design, identify any
environmental validation limitation precisely, and do not report the lab as
runtime-validated unless all requested live checks actually pass.
