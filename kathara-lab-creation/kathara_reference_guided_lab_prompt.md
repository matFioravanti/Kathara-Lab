# Kathara Reference-Guided Lab Generation Prompt

You are working inside a Kathara lab repository.

Your task is to design, generate, review, or fix Kathara laboratory scenarios while relying on authoritative documentation and existing repository examples whenever any structural, syntactic, configuration, or implementation detail is uncertain.

## Primary Reference Sources

Before making assumptions about Kathara behavior, syntax, commands, file structure, device configuration, or validation procedures, consult the relevant official documentation linked in the local `SKILL.md` file.

Treat the following documentation as authoritative:

- Kathara command reference:  
  https://www.kathara.org/man-pages/kathara.1.html

- `lab.conf` reference:  
  https://www.kathara.org/man-pages/kathara-lab.conf.5.html

- Lab lifecycle commands:
  - `kathara lstart`:  
    https://www.kathara.org/man-pages/kathara-lstart.1.html
  - `kathara linfo`:  
    https://www.kathara.org/man-pages/kathara-linfo.1.html
  - `kathara lrestart`:  
    https://www.kathara.org/man-pages/kathara-lrestart.1.html
  - `kathara lclean`:  
    https://www.kathara.org/man-pages/kathara-lclean.1.html

- Device interaction commands:
  - `kathara connect`:  
    https://www.kathara.org/man-pages/kathara-connect.1.html
  - `kathara exec`:  
    https://www.kathara.org/man-pages/kathara-exec.1.html

- Environment validation:
  https://www.kathara.org/man-pages/kathara-check.1.html

- Official Kathara Docker images:
  https://github.com/KatharaFramework/Docker-Images/tree/develop

- Official Kathara lab examples:
  https://github.com/KatharaFramework/Kathara-Labs

When a command supports `--help`, use it when necessary to confirm the exact accepted syntax.

If the official documentation conflicts with assumptions, memory, generated patterns, or existing local examples, follow the official documentation.

## Local Reference Repository

Inspect the complete local folder:

```text
kathara-lab-exercises/
```

Use all relevant files and subdirectories inside this folder as implementation references.

Study the existing labs to understand:

- directory naming conventions;
- laboratory folder structure;
- `lab.conf` syntax and topology declarations;
- device and interface numbering;
- collision-domain naming conventions;
- `.startup` file structure;
- IPv4 and IPv6 addressing conventions;
- static routing configuration;
- router forwarding configuration;
- DNS server configuration;
- web server configuration;
- client configuration;
- service startup procedures;
- device image selection;
- persistent files stored inside device directories;
- README and exercise documentation conventions;
- validation commands;
- expected differences between hosts, routers, switches, DNS servers, and application servers.

Do not inspect only one example. Compare multiple relevant labs before deciding that a pattern is a repository convention.

## Reference Resolution Procedure

Whenever you have any doubt about how part of the lab should be structured or configured, follow this exact order:

1. Identify the uncertain element precisely.
2. Read the relevant section of the local `SKILL.md`.
3. Open the relevant official documentation link.
4. Search `kathara-lab-exercises/` for labs implementing the same or a similar feature.
5. Compare at least two examples when available.
6. Determine whether the examples represent:
   - a Kathara requirement;
   - a repository convention;
   - a scenario-specific implementation choice.
7. Use the official documentation for required behavior.
8. Use the local examples for repository style and established implementation patterns.
9. Record any unavoidable assumption explicitly before applying it.

Do not invent Kathara syntax, command-line options, configuration directives, paths, service commands, or file naming rules.

## Lab Structure Rules

Use the canonical Kathara layout when applicable:

```text
<lab-name>/
├── lab.conf
├── <device>.startup
├── <device>/
│   └── ...
├── shared/
├── images/
└── README.md
```

Only create optional folders when they are actually required.

Remember:

- `lab.conf` defines devices, interfaces, collision domains, images, and lab-level topology information.
- A collision-domain label does not configure an IP address or a route.
- IP addresses, routes, forwarding, and services must be configured inside startup files or persistent device files.
- Device interface numbering must match the numbering declared in `lab.conf`.
- Keep interface indexes contiguous unless the documentation or an existing repository convention requires otherwise.
- Kathara interfaces are already enabled at startup; do not add unnecessary `ip link set ... up` commands.
- Interactive changes made after `kathara lstart` are temporary and must not replace persistent lab configuration.

## Configuration Rules

Prefer the `ip` command for:

- IPv4 and IPv6 address assignment;
- route creation;
- interface inspection.

Use `systemctl` for service management when the selected image supports and expects it.

Use suitable validation tools where relevant:

- `ping` for network reachability;
- `traceroute` for path verification;
- `curl` for HTTP or application-level verification;
- `tcpdump` for packet-level diagnosis;
- `ip addr show` for interface validation;
- `ip route show` for routing-table validation;
- `systemctl status <service>` for service validation.

Select device images according to the required service. Confirm the image and available software using `SKILL.md`, the official Docker image repository, and matching examples from `kathara-lab-exercises/`.

## Required Analysis Before File Generation

Before generating or modifying a lab:

1. Restate the requested topology.
2. List all devices and their roles.
3. Define every link and collision domain.
4. Define the interface mapping for every device.
5. Define the complete addressing plan.
6. Define the routing strategy and all required static routes.
7. Define all required services.
8. Select the appropriate Kathara image for every device.
9. Identify the existing labs used as references.
10. Identify the official documentation sections used to resolve uncertain details.
11. List explicit assumptions.
12. Check for address conflicts, missing routes, inconsistent interfaces, and unsupported service configurations.

Do not generate files until the design is internally consistent.

## Implementation Requirements

When generating the lab:

- create all required files;
- keep names deterministic and consistent;
- use repository conventions discovered in `kathara-lab-exercises/`;
- write idempotent startup commands where reasonably possible;
- persist service configuration inside the appropriate device directories;
- configure all intended behavior through lab files;
- avoid manual-only configuration steps;
- avoid copying irrelevant configuration from reference labs;
- adapt examples to the new topology instead of duplicating them blindly;
- preserve the requested protocol version, addressing type, routing method, and validation goal.

## Validation Procedure

After generating or modifying the lab, validate it through separate commands.

Run each step independently and inspect its output before continuing:

1. `kathara check`
2. `kathara lstart`
3. `kathara linfo`
4. For every device:
   - `kathara exec <device> -- ip addr show`
   - `kathara exec <device> -- ip route show`
5. Test each directly connected link with targeted `ping` commands.
6. Test end-to-end reachability.
7. Run `traceroute` when the expected route must be confirmed.
8. Verify every required service with `systemctl status <service>`.
9. Run protocol-specific tests such as DNS lookups or HTTP requests.
10. If validation fails:
    - isolate the first failing layer;
    - inspect the relevant local examples;
    - consult the relevant official documentation;
    - fix the persistent lab files;
    - rerun the failed step;
    - continue only after the step succeeds.
11. Run `kathara lclean`.
12. Start the lab again with `kathara lstart`.
13. Run `kathara linfo` again to confirm that the scenario restarts reliably.

Never treat an interactive temporary fix as a completed solution.

## Reporting Requirements

At the end of the task, provide:

- a concise summary of the generated or modified lab;
- the final topology;
- the addressing plan;
- the routing plan;
- the selected images;
- the services configured;
- the local reference labs consulted;
- the official documentation consulted;
- all assumptions made;
- all files created or modified;
- the validation commands executed;
- the result of each validation step;
- any unresolved limitation or ambiguity.

## Core Decision Rule

When uncertain, do not guess.

Consult the official Kathara documentation first, then compare the relevant implementations inside `kathara-lab-exercises/`, and only then choose the configuration that is both technically correct and consistent with the repository.
