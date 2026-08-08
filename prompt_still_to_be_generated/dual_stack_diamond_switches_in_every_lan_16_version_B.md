# Kathara laboratory generation specification

    ## Identity

    - Collection: `small_prompts_simple_natural_language2`
    - Scenario: 16
    - Version: B
    - Difficulty: Medium
    - Main concepts: dual-stack, IPv4, IPv6, diamond topology, four routers, switches, many PCs
    - Final lab folder name: `dual_stack_diamond_switches_in_every_lan_16_version_B`
    - Target: create exactly one self-contained Kathara laboratory using the folder name above.

    ## Authoritative scenario request

    Build a lab with four routers in a diamond shape. Each router has one LAN with a switch and four PCs behind the switch. Use both IPv4 and IPv6 on everything. Write all routes by hand for both protocols. Every PC must reach every other PC on both IPv4 and IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.

    ## Operating constraints

    Use the `Skill.md` in the `kathara-lab-creation` folder as the authoritative implementation guide. Follow its conventions for topology, `lab.conf`, startup scripts, device filesystems, images and validation.

    - Generate exactly one complete laboratory.
    - Do not create a second nested laboratory.
    - Do not leave placeholders, unresolved assumptions, dummy addresses, incomplete routes or unfinished service files.
    - Do not use dynamic routing protocols.
    - Keep interface numbering contiguous from `eth0`.
    - Treat collision-domain names as Layer-2 labels only.
    - Configure all intended state persistently in the generated lab files.
    - Kathara interfaces are already active at boot; do not add unnecessary `ip link set ... up`.
    - Prefer idempotent commands such as `ip address replace` and `ip route replace`.
    - Enable forwarding only on routers and only for the required address families.
    - Use `systemctl` for service management.
    - Do not run Kathara or the checker while generating the files.

    ## Required design work

    Derive and implement a deterministic design that includes:

    1. Every router, client, server, switch and transit role.
    2. Every router-to-router and LAN collision domain.
    3. Complete interface-to-domain mapping.
    4. A complete, non-overlapping address plan.
    5. Complete static routing tables for all routers and end hosts.
    6. Deterministic path selection where redundant paths exist.
    7. Exact DNS roles, zones, delegation, forwarding and records where required.
    8. Exact HTTP roles, domain names and deterministic test content where required.
    9. Explicit positive and negative routing behavior for selective-connectivity scenarios.
    10. Verification of all maximum-degree and topology constraints.

    ## Addressing policy

    - Use deterministic dual-stack addressing.
- IPv4: distinct `/24` LANs from `10.42.16.0/16` and distinct `/30` router links from `172.42.16.0/24`.
- IPv6: distinct `/64` LANs under `2001:db8:2010::/48` and distinct `/64` router links under `2001:db8:2010:ff00::/56`.
- Use `.1`/`::1` on router LAN interfaces and assign hosts sequentially from `.10`/`::10`.
- Configure and validate both address families independently.

    Assign subnet indices in topology order and document the complete mapping in `README.md`.

    ## Runtime images

    - Use `kathara/core:latest` for ordinary routers and clients unless a service-specific image is required.
- Implement Ethernet switches as dedicated Layer-2 software bridge devices without routed IP addresses unless explicitly required.

    ## Required files

    Generate at least:

    - `lab.conf`;
    - one `<device>.startup` file for every device requiring startup configuration;
    - one persistent `<device>/` filesystem directory for every DNS, HTTP, bridge or other service requiring configuration;
    - `README.md`.

    `README.md` must include:

    - objective and topology description;
    - device/interface table;
    - collision-domain table;
    - IPv4/IPv6 addressing table;
    - static-route table for every router;
    - service-role and DNS-record tables where applicable;
    - expected traffic paths where multiple paths exist;
    - positive and negative connectivity expectations;
    - `kathara lstart` and `kathara lclean`;
    - exact `kathara exec` validation commands.

    ## `lab.conf` requirements

    - Declare every device exactly once.
    - Use contiguous interface numbers.
    - Attach every interface to the intended collision domain.
    - Set an explicit image for every device.
    - Set IPv4/IPv6 feature flags consistently.
    - Add concise lab metadata.
    - Do not encode IP configuration in collision-domain labels.

    ## Startup and service requirements

    - Assign all addresses statically.
    - Add every required host default route and router static route.
    - Do not introduce prohibited default routes.
    - Ensure return paths exist for every required communication.
    - Configure deterministic routes where redundant links exist.
    - Configure software bridges persistently for switches.
    - Configure DNS resolver files, zones, delegations, forwarders, A/AAAA records and service startup persistently.
    - Configure HTTP content and Apache startup persistently.
    - Ensure each startup file refers only to interfaces declared for that same device.
    - For selective-access scenarios, enforce non-reachability deliberately through routing-table design and document it.

    ## Validation requirements

    The lab must be designed so that, after `kathara lstart`:

    - every declared device starts;
    - all expected addresses and routes are present;
    - directly connected peers communicate;
    - every required end-to-end ping succeeds;
    - every prohibited reachability check fails for the intended routing reason;
    - DNS lookups return the required A and/or AAAA records;
    - full DNS chains follow the intended hierarchy;
    - HTTP requests return a successful response;
    - IPv4 and IPv6 are tested separately in dual-stack scenarios;
    - route and traceroute checks confirm deterministic forwarding where multiple physical paths exist.

    Include exact commands for `ip addr`, `ip route`, `ping`, `traceroute`, `dig` and `curl` where applicable.

    ## Completion criteria

    The output is complete only when:

    - the topology exactly satisfies the scenario;
    - every requested device and service is implemented;
    - all routing is static;
    - positive and negative reachability requirements are explicit;
    - all files are internally consistent;
    - no placeholder remains;
    - the resulting folder is ready for `kathara lstart`.
