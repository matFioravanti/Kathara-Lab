# Candidate-independent evaluation plan

## Resolution rules

The evaluator must first resolve a single IPv4 address plan and topology inventory from the candidate lab: the Kathara-safe identifiers that implement R1--R5; the ten PC identifiers and their owning router LANs; every collision domain and endpoint interface; every IPv4 interface address/prefix; and each PC's IPv4 address.  These are values to bind into checks, not additional requirements or preferred naming/addressing choices.

For routing, derive, for each router, the set of **remote IPv4 subnets** as every IPv4 subnet in that resolved plan which is not directly connected to that router.  The prompt does not prescribe a path where multiple paths exist (notably between R1 and R4), so a check must never freeze a particular next hop or egress interface unless it is required by the resolved route itself.  It must require a route for the exact destination prefix and allow any valid non-default next hop.

`lab_inline` must use the resolved candidate identifiers/interfaces and collision-domain names.  Its comparison is exact: no missing required device, endpoint, or required link, and no topology that changes the required device-to-link mapping.  The original labels R1--R5 are semantic router roles; their actual checker-safe device identifiers must be resolved because uppercase labels cannot be used directly as Kathara identifiers.

## Requirement mapping

| Evaluation requirement | Checker category/block | Validation strictness | Concrete values to resolve later |
|---|---|---|---|
| Five routers: R1, R2, R3, R4, R5 | `lab_inline` | Exact device existence and role-to-topology mapping | Checker-safe identifiers implementing R1--R5; each router's interface indices. |
| Each router serves one LAN containing two PCs | `lab_inline` | Exact LAN membership: one distinct LAN per router, with that router and exactly its two PCs as required endpoints | The five LAN collision-domain names; the two PC identifiers on each LAN; router/PC interface indices. |
| Ten PCs in total | `lab_inline` | Exact required PC inventory and LAN attachment | All ten PC identifiers and their two-per-router assignment. |
| R1 connects to R2 and R3 | `lab_inline` | Exact point-to-point adjacency; no substituted intermediate device | R1/R2/R3 identifiers, the two collision-domain names, and endpoint interface indices. |
| R2 connects to R4 | `lab_inline` | Exact point-to-point adjacency | R2/R4 identifiers, collision-domain name, endpoint interface indices. |
| R3 connects to R4 | `lab_inline` | Exact point-to-point adjacency | R3/R4 identifiers, collision-domain name, endpoint interface indices. |
| R4 connects to R5 | `lab_inline` | Exact point-to-point adjacency | R4/R5 identifiers, collision-domain name, endpoint interface indices. |
| IPv4 only | `ip_mapping` plus `custom_commands` | `ip_mapping` checks every resolved IPv4 address and prefix exactly.  Custom read-only IPv6 inventory checks must reject configured non-loopback/non-link-local IPv6 addresses and non-link-local IPv6 routes on every router and PC; automatic link-local IPv6 state is not treated as an IPv6 network design. | Every device identifier; every IPv4 interface/index/address/prefix; the exact command assertions used to produce an empty prohibited-IPv6 inventory. |
| Every router has a fully explicit routing table | `kernel_routes` plus `custom_commands` | For each router, exact coverage of the derived remote-subnet set: one route for every exact remote destination prefix, with next hop/interface intentionally unconstrained where multiple valid paths exist.  A per-prefix read-only custom assertion must additionally require the selected kernel route to be `proto static`; this is necessary because `kernel_routes` cannot distinguish static from dynamically learned routes. | Router identifiers; all IPv4 prefixes; directly connected prefix set per router; resulting remote-prefix set per router; for each resolved route, its observed route representation sufficient to assert `proto static` (but not a mandated path). |
| Every router has a specific static route for every remote subnet | `kernel_routes` plus `custom_commands` | Exact destination-prefix matching for every derived remote subnet, and exact static route origin (`proto static`).  No BGP/OSPF/RIP configuration or fixed next hop is asserted because neither is required by the prompt. | Same routing inventory as above, including each router's remote prefixes and route command/regex bindings. |
| No router contains a default route | `custom_commands` | Exact negative assertion on each router: the IPv4 default-route query must produce no route.  A custom command is required because the schema has no negative `kernel_routes` assertion. | Router identifiers and the standard read-only IPv4 default-route query/assertion. |
| All ten PCs can reach one another | `reachability` | Full directed mesh: for every PC, require ICMP reachability to the IPv4 address of each of the other nine PCs (90 assertions). | Ten PC identifiers and one resolved IPv4 address per PC to use as the ping target. |

## Non-applicable blocks

Do not add `daemons`, `protocols`, protocol `injections`, DNS, HTTP, or startup-file assertions.  The prompt mandates static routing but does not mandate a routing daemon, a particular static-route configuration mechanism, services, or startup-file layout.  The custom checks above are limited to the two gaps that supported standard blocks cannot express: static route origin and the absence of default/IPv6 routing.
