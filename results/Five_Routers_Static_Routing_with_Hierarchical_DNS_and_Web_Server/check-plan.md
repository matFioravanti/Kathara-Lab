# Frozen evaluation strategy

This plan is candidate-independent.  Names such as `router_1`, `client`, and
`root_dns` below are placeholders for values to resolve at evaluation time;
they are not required candidate names.  No topology, address plan, daemon
implementation, or HTTP service is implied beyond the scenario requirements.

| ID | Requirement | Checker category/block | Validation strictness | Concrete values to resolve later from the candidate lab |
| --- | --- | --- | --- | --- |
| N1 | The lab contains five routers. | Not checkable with the supported checker schema. `lab_inline` can assert one *predefined* device-to-link topology, but has no cardinality, role, or device-type predicate. | N/A | N/A. Do not turn the candidate's discovered router names into `lab_inline`: that would check a candidate-specific topology rather than the required count. |
| N2 | Each router has maximum degree three. | Not checkable with the supported checker schema. `lab_inline` only performs exact matching against a prescribed topology; it cannot assert a maximum degree over an otherwise unspecified topology. | N/A | N/A. |
| N3 | Routing is configured statically. | `test.kernel_routes` | Exact route matching: for every required non-connected route, require the exact destination prefix and its static next hop **or** outgoing `ethN` interface, using the supported one-path route form. Do not assert routing daemons or negative daemon checks: neither a daemon choice nor an exhaustive list of prohibited daemons is specified. | Router device names; each router's intended static route destination prefix; the required next-hop IPv4 address or outgoing interface; and any host default routes needed for the stated end-to-end path. Exclude directly connected prefixes. |
| D1 | The network contains a root DNS server. | `test.applications.dns.authoritative` | Exact authority matching for the root zone (`.`): require the resolved root DNS server IP as an authoritative server. | Root DNS device name (for identification only), root DNS server IP, and the root zone it serves (`.`). |
| D2 | The network contains an organization DNS server. | `test.applications.dns.authoritative` | Exact authority matching: require the organization DNS server IP as authoritative for the organization zone. | Organization DNS device name, organization DNS server IP, and the organization zone. The zone must be resolved from the DNS delegation/configuration, not guessed from a device name. |
| D3 | The network contains a local name server. | `test.applications.dns.local_ns` | Exact resolver assignment: the resolved local-name-server IP must be the configured local resolver for the resolved client device. | Local DNS device name, local DNS server IP, and client device name. |
| S1 | The lab contains a server named `kathara.org`. | `test.applications.dns.records` (A record) | Exact DNS-record matching: require `kathara.org` to have an A record containing the resolved server IPv4 address. | Server device name, server IPv4 address, and the authoritative DNS zone/server hosting the record. The record owner is fixed by the prompt as `kathara.org`. |
| S2 | The lab contains a client. | `test.reachability` | Exact source-device selection: execute the required name-based reachability assertion from the resolved client device. | Client device name. |
| S3 | The client can reach the server using the server's name. | `test.reachability` | Exact matching: from the resolved client device, require reachability to the literal DNS target `kathara.org`. This validates name resolution and IP-layer reachability together. | Client device name; the server IPv4 address may be resolved for cross-checking against S1, but the reachability target remains the literal `kathara.org`. |

## Fixed exclusions

- Do not use `lab_inline`: the prompt supplies neither router/device identifiers nor a device-to-link mapping, and an exact candidate-derived topology would not be a shared evaluation requirement.
- Do not use `test.ip_mapping`: no interface addresses or prefixes are specified.
- Do not use `test.daemons`: DNS and static routing are requirements, but no particular DNS implementation or daemon is mandated.
- Do not use `test.applications.http`: the prompt requires a server reachable by name, not an HTTP service or status code.
- Do not use `custom_commands`: standard blocks cover every representable semantic requirement; topology count and maximum degree have no safe, candidate-independent representation in the supported schema.

## Fixed checker-wide settings

- `default_image`: use the schema fallback `kathara/frr`, because the prompt specifies no image.
- `convergence_time`: 10 seconds, the prescribed static-only value.
