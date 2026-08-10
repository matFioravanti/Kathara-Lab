# Check Plan

This plan is frozen from the evaluation specification. Device names, collision-domain names, interface numbers, IPv4 addresses/prefixes, subnet prefixes, and next hops are resolved later from the candidate lab only to instantiate these checks; they do not change the requirements below.

| Evaluation requirement | Checker category/block | Validation strictness | Concrete values to resolve later from the candidate lab |
| --- | --- | --- | --- |
| 1. Exactly five routers with the R1--R5 roles | `lab_inline` topology declaration | Exact: require exactly five router devices occupying the five required roles; reject an absent role or an additional router. | Candidate router device identifiers corresponding to R1, R2, R3, R4, and R5; each router's interface numbers. |
| 2. Required router-to-router links | `lab_inline` topology declaration | Exact: require the five links R1--R2, R1--R3, R2--R4, R3--R4, and R4--R5, and no additional router-to-router link. | Collision-domain names and the interface number used by each endpoint. |
| 3. One distinct LAN per router | `lab_inline` topology declaration | Exact: each router has one LAN collision domain distinct from all router-to-router collision domains and from every other router LAN. | LAN collision-domain name and the serving router interface for each router role. |
| 4. Two PCs on every router LAN; ten PCs total | `lab_inline` topology declaration | Exact: each of the five LANs contains its serving router and exactly two PCs, for exactly ten PCs overall; reject extra PCs or a PC attached to the wrong LAN. | PC device identifiers, their LAN membership, and interface numbers. |
| 5. IPv4 only | `ip_mapping` plus `custom_commands` | Exact for configured network-layer addressing: all expected interface addresses are IPv4 addresses, and custom runtime assertions reject configured non-link-local IPv6 addresses or IPv6 routes. IPv6 link-local artifacts not introduced by the lab are not treated as a violation. | Every device's IPv4 address/prefix by interface; the device list for the IPv6 runtime assertions. |
| 6. Fully explicit routing table on every router | `kernel_routes` plus `custom_commands` | Exact: the explicit non-connected route set on each router must consist of the required remote-subnet entries, with no required remote subnet omitted. Custom assertions verify the expected number of static entries. | For each router: directly connected subnets, remote subnet prefixes, expected number of remote routes, route next hop, and outgoing interface. |
| 7. Specific static route for every remote subnet on every router | `kernel_routes` plus `custom_commands` | Exact: assert every remote prefix with its required next hop and/or outgoing interface in `kernel_routes`; one custom assertion per expected route verifies that the installed route is static. Directly connected subnets are excluded from `kernel_routes`. | For each router and remote subnet: destination prefix, next-hop IPv4 address, egress interface, and the command/output pattern proving `proto static`. |
| 8. No default route on any router | `custom_commands` | Exact prohibition: on each router, a command asserting that `ip -4 route show default` returns no route must succeed. | Router device identifiers. |
| 9. Every PC reaches every other PC | `reachability` | Exact all-pairs PC connectivity: for each PC, list the IPv4 address of each of the other nine PCs; self-reachability is not required. | The ten PC device identifiers and each PC's IPv4 address. |

## Checker representation notes

- `lab_inline` is instantiated with topology-only device/interface-to-collision-domain mappings; image declarations are not included.
- `kernel_routes` is used only for explicit routes, never directly connected subnets. Its route entries include next-hop and/or interface assertions where resolved.
- `custom_commands` is necessary because the supported `kernel_routes` block represents expected routes but does not by itself express the prohibition of a default route or the required static route origin.
