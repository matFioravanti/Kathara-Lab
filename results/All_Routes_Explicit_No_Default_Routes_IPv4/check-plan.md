# Checker plan

This plan instantiates the requirements in `evaluation-spec.md` from the candidate lab without changing their scope.  Role labels R1–R5 refer to the routers required by the scenario; candidate device identifiers, interfaces, collision-domain names, addresses, prefixes, and next hops must be resolved from the candidate lab.

## R1 — Router topology

- Checker category/block: `lab_inline` (or `structure`) topology declaration.
- Validation strictness: exact.  Declare exactly five router devices mapped to the R1–R5 roles and exactly the five required inter-router collision domains/connections; reject an extra or missing inter-router connection.
- Candidate values to resolve: the device identifier for each router role; each router-facing interface number; the collision-domain name used for each of the five required links; and the candidate's distinction between router-facing and LAN-facing interfaces.

## R2 — LANs and PCs

- Checker category/block: `lab_inline` (or `structure`) topology declaration; `requiring_startup` for the ten PC devices.
- Validation strictness: exact topology cardinality and membership.  Require one distinct LAN collision domain per router, exactly two PCs on each LAN, and no PC attached to a router other than the router serving that LAN.  Require a startup file for every resolved PC device.
- Candidate values to resolve: the two PC device identifiers for each router LAN; each PC and router LAN-facing interface number; the five LAN collision-domain names; and the device identifiers of all ten PCs.

## R3 — IP protocol version

- Checker category/block: `ip_mapping` plus `custom_commands`.
- Validation strictness: exact for assigned interface addresses and strict absence for IPv6 global addressing.  Require the resolved IPv4 address/prefix on every configured non-loopback interface and require each device to report no global IPv6 addresses.
- Candidate values to resolve: every device identifier; every configured interface number; every IPv4 address/prefix; and the command assertion representation that verifies an empty global-IPv6 address listing on each device.

## R4 — Explicit static routing

- Checker category/block: `kernel_routes` plus `custom_commands`.
- Validation strictness: exact.  For each router, require one specific route, with the resolved next hop and outgoing interface, for every subnet not directly connected to it; require no extra non-connected routes.  Custom commands must verify that every required non-connected route is installed as a static route rather than by a routing daemon or another route source.
- Candidate values to resolve: router identifiers; the complete IPv4 subnet inventory; the directly connected subnet set for each router; the remote-subnet set for each router; each required route prefix, next-hop IPv4 address, and outgoing interface; and command assertions that identify each route as static.

## R5 — No default routes

- Checker category/block: `custom_commands`.
- Validation strictness: strict absence.  On every router, assert that the IPv4 routing table contains no `default` route and no `0.0.0.0/0` route.
- Candidate values to resolve: router device identifiers and the concrete empty-output assertion for the IPv4 default-route query.

## R6 — End-to-end PC connectivity

- Checker category/block: `reachability`.
- Validation strictness: exhaustive directed full mesh.  For each PC, require ping reachability to every other PC's resolved IPv4 address; self-reachability is not required.
- Candidate values to resolve: the ten PC device identifiers and one reachable IPv4 address for each PC.
