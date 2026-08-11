# Check plan

## R01 — Five routers

- Checker category/block: `lab_inline` topology declaration.
- Validation strictness: exact cardinality of five router devices and exact one-to-one assignment to the R1–R5 router roles.
- Values to resolve from the candidate lab: router machine names and their interface-to-collision-domain mappings.

## R02 — Required router-to-router topology

- Checker category/block: `lab_inline` topology declaration.
- Validation strictness: exact presence of the five required direct adjacencies: R1–R2, R1–R3, R2–R4, R3–R4, and R4–R5; no substituted router adjacency satisfies this requirement.
- Values to resolve from the candidate lab: the router machine names, interface numbers, and collision-domain names that implement each adjacency.

## R03 — One LAN per router

- Checker category/block: `lab_inline` topology declaration.
- Validation strictness: exact cardinality of one distinct PC-serving LAN for each router role; each LAN is directly attached to its associated router.
- Values to resolve from the candidate lab: LAN collision-domain names, router LAN interfaces, and the router role associated with each LAN.

## R04 — Two PCs on every router LAN and ten PCs in total

- Checker category/block: `lab_inline` topology declaration.
- Validation strictness: exactly two PC devices are attached to each required router LAN, for an exact total of ten PCs; no PC is counted for more than one LAN.
- Values to resolve from the candidate lab: PC machine names, their interfaces, and their LAN collision-domain memberships.

## R05 — IPv4 only

- Checker category/block: `custom_commands`.
- Validation strictness: strict prohibition of globally configured IPv6 addresses and IPv6 forwarding/routing configuration on every router and PC; IPv4 is the only configured network-layer protocol used for the lab.
- Values to resolve from the candidate lab: all router and PC machine names.

## R06 — Explicit static route for every remote subnet

- Checker category/block: `kernel_routes` plus `custom_commands`.
- Validation strictness: exact route coverage on each router. For every IPv4 subnet that is not directly connected to that router, require one specific route with the resolved destination prefix, next hop, and egress interface; verify that every required route is static and that no required remote subnet is omitted.
- Values to resolve from the candidate lab: all IPv4 subnet prefixes, each router's directly connected subnets, every router's remote-subnet set, and the destination prefix, next hop, egress interface, and static-route evidence for each required route.

## R07 — No router default routes

- Checker category/block: `custom_commands`.
- Validation strictness: strict absence of an IPv4 default route on every router, including routes expressed as `default` or `0.0.0.0/0`.
- Values to resolve from the candidate lab: router machine names.

## R08 — Full PC-to-PC reachability

- Checker category/block: `reachability`.
- Validation strictness: complete directed reachability matrix: each of the ten PCs must successfully ping each of the other nine PCs, for 90 required source-to-destination checks.
- Values to resolve from the candidate lab: PC machine names and the IPv4 address used for each PC reachability target.
