# Evaluation Specification

## Scope

This specification freezes only the requirements stated in `input/prompt.md`. It does not select device names, collision domains, addresses, routes, DNS implementation, HTTP implementation, images, files, or any other omitted detail.

The requested deliverable is a detailed prompt for a Kathará lab. The scenario described by that prompt has the requirements below.

## Frozen Requirements and Evaluation Strategy

| ID | Requirement | Checker category and strategy | Candidate-independent evaluation rule |
| --- | --- | --- | --- |
| R1 | The deliverable is a detailed prompt for the requested lab. | No supported checker category; omit assertion. | The supplied checker schema evaluates running Kathará lab properties, not the completeness or format of a prompt file. No `custom_commands` assertion is eligible because no prompt-file path or required content is specified. |
| R2 | The lab contains exactly five routers. | No supported checker category; omit assertion. | `lab_inline` checks an explicit device-to-link mapping, but the prompt supplies neither router identifiers nor a link mapping. The schema has no router-count assertion. A topology assertion cannot be instantiated without inventing identifiers. |
| R3 | Each router has a maximum topology degree of three. | No supported checker category; omit assertion. | Degree can only be determined from an explicit `lab_inline` collision-domain mapping. Because the prompt specifies no links or collision domains, no candidate-independent topology mapping or degree assertion can be configured. |
| R4 | Network routing is static routing. | Checker: `kernel_routes`; category: routing-table/data-plane. Omit assertion. | `kernel_routes` can check only explicitly expected static routes and their optional next hops or interfaces. The prompt gives no prefixes, routes, gateways, interfaces, or router identities. No routing protocol or daemon assertion is implied by static routing. |
| R5 | The network has three DNS servers: a root DNS server, an `org` DNS server, and a local name server. | Checker: `test.applications.dns`; categories: DNS authority and local resolver. Omit assertions. | `applications.dns.authoritative` requires each zone’s authoritative-server IP address; `applications.dns.local_ns` requires the resolver IP and the names of devices that use it. None of those values is stated. The roles alone do not authorize an IP, device-name, daemon, or DNS implementation assumption. |
| R6 | A server is available as `kathara.org`. | Checker: `test.applications.dns.records`; category: DNS record. Omit assertion. | A DNS record assertion requires a record type and expected value. The prompt supplies the name but not its record type or address. It also does not explicitly require HTTP or any particular server daemon, so neither `applications.http` nor `daemons` is applicable. |
| R7 | A client can reach the `kathara.org` server using its name. | Checker: `test.reachability`; category: end-to-end reachability. Omit assertion. | `reachability` requires a source device name and a target IP address or DNS name. Although `kathara.org` is a stated target name, the client device name is not specified; the schema has no existential “some client” check. Adding a source device would be an invented topology requirement. |

## Checker Configuration Constraints

- `default_image` is mandatory in the eventual checker configuration. Since the prompt does not specify a Kathará image, use only the schema-defined checker fallback when that configuration is instantiated; this is not a scenario requirement.
- Use the static-only convergence time of 10 seconds if a checker configuration is instantiated.
- Do not add `lab_inline`, `requiring_startup`, `ip_mapping`, `daemons`, `kernel_routes`, DNS, HTTP, reachability, protocol, or custom-command assertions beyond the requirements and values frozen above.
