---
name: kathara-lab-checker
version: framework-automatic-1
purpose: Generate one candidate-independent correction.yaml from a structured Kathara prompt.
---

# Kathara Lab Checker — Automatic Framework Mode

Generate exactly one canonical `correction.yaml` for `kathara-lab-checker==0.1.14`.
This Skill is used by an automated paired experiment. There is no interactive user-selection step.

## Authoritative inputs

In framework mode you may use only:

1. `input/prompt.md` — the scenario specification;
2. `resources/skills/checker/SKILL.md` — this policy;
3. `resources/checker/config-schema.md` — supported configuration syntax.

Candidate laboratories are intentionally unavailable. Never derive checks from a generated lab, its
`lab.conf`, `.startup` files, logs, manifests, reports, or another correction. The same correction must be fair for both `with_skill` and `without_skill` candidates.

## Core rule

For every requirement explicitly stated or unambiguously and deterministically derivable from the prompt:

1. prefer a standard checker block when one represents the requirement;
2. configure expected values only from the prompt;
3. never assume an implementation choice that the prompt leaves open;
4. never invent a test merely to increase coverage;
5. if a requirement cannot be represented reliably, omit that assertion rather than guessing.

The correction evaluates **what the prompt requires**, not **how a candidate happened to implement it**.

## Automatic mapping

Include an applicable block automatically; do not ask the user which checks to select.

- Expected topology / device-to-link mapping -> `lab_inline`.
- Devices explicitly required to use startup scripts -> `test.requiring_startup`.
- Explicit/static interface addresses -> `test.ip_mapping`.
- Explicitly required services/daemons, or daemons unambiguously implied by an explicitly mandated protocol -> `test.daemons`.
- Static/default or dynamically learned routes explicitly expected by the scenario -> `test.kernel_routes`.
- BGP requirements -> `test.protocols.bgpd`.
- RIP requirements -> `test.protocols.ripd`.
- OSPF requirements -> `test.protocols.ospfd`.
- Explicit redistribution -> the corresponding `injections` block.
- DNS authority/resolver/record requirements -> `test.applications.dns`.
- HTTP requirements -> `test.applications.http`.
- Required end-to-end connectivity -> `test.reachability`.

Do not add negative daemon assertions unless the prompt explicitly requires a daemon not to run.
Do not force a specific routing protocol, service implementation, file layout, or daemon when the prompt
allows multiple valid solutions.

## Derivation rules

### `default_image`

`default_image` is mandatory and must always be included in `correction.yaml`.

If the scenario explicitly specifies a Kathara image, use that image.
If the scenario does not specify an image, use the fallback defined by
`resources/checker/config-schema.md`.

The fallback image is a technical checker requirement and must not be
interpreted as an additional scenario requirement.


### `lab_inline`

Use topology-only `device[index]="collision-domain"` mappings.
Do not include image declarations. Prefer `lab_inline`; do not emit
`structure` and do not emit `labs_path`.

Kathara identifier constraints:

- Device identifiers must match `[a-z0-9_]{1,30}`.
- Device identifiers may contain lowercase letters, digits, and underscores.
- Device identifiers must not contain uppercase letters, hyphens, spaces, or other special characters.
- Collision-domain identifiers may contain letters, digits, and underscores.
- Collision-domain identifiers must not contain hyphens, spaces, or other special characters.

Examples:

- Valid device identifiers: `r1`, `pc11`, `router_1`
- Invalid device identifiers: `R1`, `PC11`, `router-1`
- Valid collision domains: `net12`, `net_12`, `r1_r2`
- Invalid collision domains: `r1-r2`, `client lan`

When constructing `lab_inline` from a candidate lab, preserve the actual
candidate topology while ensuring the emitted identifiers are valid for the
Kathara parser.

### `requiring_startup`

List only devices for which a startup file is explicitly required or is an unambiguous structural
requirement of the structured prompt. Do not infer from candidate files.

### `ip_mapping`

Use every interface address explicitly specified by the prompt. Runtime compatibility for checker 0.1.14:
interface keys must be `ethN` (for example `eth0`, `eth1`) when the installed checker syntax requires it,
even if older documentation shows numeric-only keys.

### `daemons`

Require only daemons explicitly named or unambiguously required by a mandated protocol/service. A negative
entry (`!daemon`) is allowed only when the prompt explicitly prohibits that daemon/service.

### `kernel_routes`

List routes explicitly installed by static configuration or expected to be learned by routing protocols.
Do not list directly connected networks merely because an interface has an address. A one-path kernel route
must identify either its gateway or its `ethN` interface, not both, for checker 0.1.14 compatibility.

### Protocols

Derive protocol values solely from the prompt. Runtime compatibility for checker 0.1.14 overrides older
Markdown examples where they conflict:

- OSPF neighbors use `router_id` / `state` where applicable;
- OSPF routes use objects containing `route`;
- OSPF interface identifiers use `ethN`;
- EVPN uses `protocols.bgpd.evpn_sessions` and `protocols.bgpd.vtep_devices`.

### Applications

DNS checks may cover authority, local resolvers, and records only when expected values are specified or
unambiguously derivable. HTTP entries use `status_code` for checker 0.1.14 (not `expected_status`).

### `reachability`

Use the connectivity goals stated by the prompt. A fully connected requirement may be expanded to the
relevant explicitly defined addresses. Do not create reachability targets from guessed addressing.

## `custom_commands` policy

`custom_commands` are a controlled fallback, not a general-purpose way to duplicate standard tests.
A custom command may be generated automatically only if **all** of these conditions hold:

1. the requirement is explicitly stated in the prompt;
2. no standard checker block represents it adequately;
3. it can be verified deterministically on a known device with a non-destructive command;
4. the expected result is known from the prompt and can be expressed through `regex_match`, `output`, or
   `exit_code`;
5. the command does not assume an implementation detail that the prompt leaves unspecified.

Always prefer a standard block over a custom command. Never duplicate `requiring_startup`, `ip_mapping`,
`daemons`, `kernel_routes`, protocol, DNS, HTTP, or `reachability` checks with custom commands.

Safe examples when explicitly required by the prompt include:

- IPv4 forwarding -> `sysctl net.ipv4.ip_forward` with a deterministic assertion;
- IPv6 forwarding -> `sysctl net.ipv6.conf.all.forwarding`;
- content of a specifically mandated file -> a read-only `grep`/`cat` assertion;
- success of a specifically mandated diagnostic command -> an `exit_code` assertion.
- Always include the mandatory `default_image` field. If the prompt does not specify a Kathara image, use the fallback `default_image` defined in the supplied schema.

Do not use destructive commands, package installation, network reconfiguration, process killing, file
modification, or commands requiring shell side effects. If a safe deterministic assertion cannot be derived,
omit the custom check.

## Convergence time

Use a deterministic value from the scenario class unless the prompt specifies one:

- static-only: 10 seconds;
- IGP (RIP/OSPF): 60 seconds;
- BGP or mixed BGP+IGP: 90 seconds.

## Output contract

Write exactly one file: `output/correction.yaml`.

- YAML only.
- No surrounding prose or Markdown fences.
- No `labs_path`.
- Prefer `lab_inline`.
- No comments are required; keep the document machine-oriented.
- Include only checker features supported by the supplied schema and the checker 0.1.14 compatibility rules above.
- Never read candidate labs.

