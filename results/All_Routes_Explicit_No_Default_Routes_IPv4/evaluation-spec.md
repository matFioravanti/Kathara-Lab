# Evaluation specification

## Scope and binding rules

This specification evaluates only the requirements stated in `input/prompt.md`. It does not prescribe collision-domain names, device-file names, interface numbering, IPv4 prefixes, host addresses, route next hops, Kathara images, routing daemons, or any service configuration.

Where a checker block needs an address, interface, collision-domain name, or device identifier that the prompt does not provide, that value must not be invented. A correction may bind such implementation values only after the frozen structural requirement has been established; the binding must not add, remove, or alter any requirement below.

## Required topology

### Five-router graph

There must be exactly five routers, denoted by the prompt as R1, R2, R3, R4, and R5, with these and only these router-to-router adjacencies:

| Router | Required router neighbours |
| --- | --- |
| R1 | R2, R3 |
| R2 | R1, R4 |
| R3 | R1, R4 |
| R4 | R2, R3, R5 |
| R5 | R4 |

Checker: `lab_inline`  
Category: topology / collision-domain mapping  
Validation: bind the candidate's router identifiers and collision-domain labels to the five required router roles, then require the adjacency pattern above. No image declaration is part of this check. The configuration schema has no generic cardinality- or role-pattern assertion, so the exact `lab_inline` mapping can be instantiated only from the candidate's otherwise-unconstrained identifiers and link labels; it must never introduce additional links or accept a different graph.

### LANs and PCs

Each router must serve exactly one LAN, and each such LAN must contain exactly two PCs. Therefore the lab must contain ten PCs in total, partitioned as two PCs on each router's LAN.

Checker: `lab_inline`  
Category: topology / collision-domain mapping  
Validation: for each router role, require one distinct LAN collision domain shared by that router and exactly two PC devices; require no PC attachment to another LAN. The schema does not support an abstract “exactly two PCs per LAN” assertion, so concrete labels must be bound without inventing them.

## Address-family requirement

The network uses IPv4 only.

Checker: no supported standard checker block  
Category: unsupported address-family constraint  
Validation: do not create `ip_mapping` entries because no IPv4 addresses or prefixes are specified. Do not use `custom_commands` to require an empty IPv6 address listing: that would impose an implementation-specific treatment of IPv6 link-local addressing not stated in the prompt. This requirement cannot be represented reliably by the supplied checker schema without adding unstated values or behavior.

## Routing requirements

### Fully explicit static routes

Every router must have a specific static route for every remote subnet, including remote LAN subnets and remote router-to-router link subnets. Directly connected subnets are not remote subnets and are not part of this requirement. Route destinations and next hops are intentionally unspecified by the prompt.

Checker: `test.kernel_routes`  
Category: kernel routing table / static remote-route coverage  
Validation: after determining the required LAN and router-to-router link subnets from the candidate's topology and IPv4 addressing, each router must have one explicit, non-default route for every subnet not directly connected to that router. Each route must be checked with its concrete gateway or `ethN` constraint only when that value is determined by the candidate's selected valid static-routing implementation. Do not list directly connected routes. The schema does not encode “route source is static” or quantify over unspecified subnets, so no candidate-derived route set may be treated as the requirement itself; the frozen requirement is complete coverage of all remote subnets.

### No default routes on routers

No router may have a default route.

Checker: `test.kernel_routes`  
Category: kernel routing table / negative default-route assertion  
Validation: the supplied `kernel_routes` schema supports required route presence but has no negative-route form. Therefore it cannot reliably assert absence of `0.0.0.0/0`. Do not invent a `custom_commands` command or parser-specific output assertion; omit a machine assertion rather than misrepresenting the schema. In particular, `0.0.0.0/0` must never be added as an expected route.

## End-to-end connectivity

All ten PCs must be able to reach every other PC.

Checker: `test.reachability`  
Category: end-to-end reachability  
Validation: require the complete pairwise PC reachability matrix: every PC must ping the IPv4 address of each of the other nine PCs. The prompt provides no PC identifiers or IPv4 addresses, so individual `reachability` targets must not be invented; they may be bound only to the ten PCs and their IPv4 addresses established by the required topology and IPv4 implementation.

## Excluded checks

Do not add assertions for startup-file presence, explicit interface addresses, images, daemons, BGP, RIP, OSPF, route redistribution, DNS, HTTP, or other services. None is explicitly required by the prompt, and the topology and routing requirements do not mandate any one such implementation.
