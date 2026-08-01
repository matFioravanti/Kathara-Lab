You are responsible for generating a large collection of small, self-contained natural-language prompts for the creation of Kathara networking labs.

Your task is NOT to create the Kathara labs themselves.

Your task is only to generate the prompts that will later be given to another AI agent responsible for creating the actual labs.

## Reference material

Before generating the prompts, inspect all files and directories contained inside:

`kathara-lab-exercises`

Use these files only as reference material to understand:

* the types of network topologies that can be requested;
* the possible combinations of routers, switches, PCs, clients and servers;
* realistic lab complexity levels;
* IPv4 and IPv6 addressing scenarios;
* static routing configurations;
* statically defined routing tables;
* DNS hierarchies and DNS resolution exercises;
* web server and client connectivity exercises;
* main server or central server architectures;
* suitable constraints for Kathara labs;
* the structure and writing style of existing lab requests.

Do not copy existing exercises verbatim. Generate new and varied lab requests inspired by the available structures.

## Objective

Generate many small prompts describing different Kathara labs in natural language.

The prompts must cover different combinations of:

* PCs;
* clients;
* routers;
* Ethernet switches;
* IPv4 networks;
* IPv6 networks;
* dual-stack IPv4/IPv6 networks;
* static routing;
* manually defined routing tables;
* default routes;
* hierarchical routing where appropriate;
* web servers;
* main or central servers;
* DNS servers;
* local DNS servers;
* root DNS servers;
* top-level domain DNS servers;
* authoritative DNS servers;
* clients resolving and contacting servers through domain names.

The generated prompts must request only static configurations.

Do not generate labs that require dynamic routing protocols such as:

* RIP;
* RIPng;
* OSPF;
* OSPFv3;
* BGP;
* IS-IS.

## Prompt pairs

For every lab scenario, generate exactly two versions of the mini-prompt.

The two versions must describe the same lab requirements, topology and expected behaviour.

### Version A

Version A must end with these exact sentences:

`Do not inspect other directories in this workspace.`

`Do not generate lab files in this step.`

### Version B

Version B must end with these exact sentences:

`Use the Skill.md in the kathara-lab-creation folder.`

`Do not generate lab files in this step.`

Do not include both directory instructions in the same mini-prompt.

Each scenario must therefore have:

* one version containing `Do not inspect other directories in this workspace.`;
* one version containing `Use the Skill.md in the kathara-lab-creation folder.`

## Mini-prompt requirements

Every mini-prompt must be:

* written in English;
* expressed in clear natural language;
* self-contained;
* precise enough for another AI to understand the requested lab;
* concise but sufficiently detailed;
* free from source code;
* free from Kathara configuration files;
* free from complete IP addressing solutions unless the scenario explicitly requires fixed addresses;
* focused on the desired topology, services and connectivity requirements;
* written as a direct instruction to generate a detailed prompt file.

Each mini-prompt should begin with a sentence similar to:

`Generate a detailed prompt file for this request:`

The AI receiving the mini-prompt must be asked to prepare a detailed specification for the lab, not to immediately create the lab files.

## Information that may be included

Depending on the scenario, each mini-prompt may specify:

* number of routers;
* maximum router degree;
* minimum router degree;
* number of switches;
* number of PCs or clients;
* number and type of servers;
* number of LANs;
* number of point-to-point router links;
* IPv4, IPv6 or dual-stack usage;
* whether all routing tables must be configured statically;
* whether default routes may be used;
* whether every router must have complete static routes;
* whether clients must reach all remote networks;
* whether specific clients must only reach selected servers;
* DNS server hierarchy;
* domain names to resolve;
* web services that must be reachable by name;
* required end-to-end connectivity;
* intended failure conditions that must not occur;
* topology constraints such as maximum router degree;
* whether redundant physical paths are allowed;
* whether the topology must be a tree, line, ring, star or partially meshed network.

Do not request dynamic routing or automatic route discovery.

## Variety requirements

Create scenarios with significantly different structures and objectives.

Include easy, medium and advanced scenarios.

The collection must include at least the following categories:

1. Simple IPv4 static routing labs.
2. Simple IPv6 static routing labs.
3. Dual-stack static routing labs.
4. Labs with one router connecting multiple LANs.
5. Labs with multiple routers arranged in a line.
6. Labs with routers arranged in a tree.
7. Labs with routers arranged in a ring.
8. Labs with a partially meshed router topology.
9. Labs containing Ethernet switches and multiple clients.
10. Labs with one central web server.
11. Labs with multiple web servers.
12. Labs with one local DNS server.
13. Labs with a root DNS server, a top-level domain DNS server and a local name server.
14. Labs with authoritative DNS servers for multiple domains.
15. Labs in which clients must reach a web server using its domain name.
16. Labs with a main server reachable from every LAN.
17. Labs where static default routes are used on edge routers.
18. Labs where every route must be explicitly defined without default routes.
19. Labs with maximum-degree constraints for routers.
20. Labs combining routing, DNS and web services.

Avoid generating many scenarios that differ only in device count. Each scenario should introduce a meaningful difference in topology, addressing family, routing strategy, service placement or connectivity requirement.

## Technical consistency

Ensure that every requested scenario is technically possible.

Before writing each prompt, internally verify that:

* the requested topology can be built;
* router-degree constraints are compatible with the requested number of links;
* every LAN can be connected to a router;
* clients have a valid path toward the required servers;
* static routing is sufficient to satisfy the connectivity requirements;
* DNS servers can reach the authoritative servers they need to query;
* clients can reach their configured DNS server;
* domain names and server placement are logically consistent;
* IPv4-only clients are not required to contact IPv6-only services;
* IPv6-only clients are not required to contact IPv4-only services unless a translation mechanism is explicitly requested;
* no dynamic routing protocol is implicitly required.

Do not solve the lab inside the mini-prompt. Describe the requirements and expected results only.

## Naming

Use varied fictional domain names and server names.

Examples may include:

* `kathara.org`;
* `example.net`;
* `network.lab`;
* `university.edu`;
* `company.test`;
* `research.org`;
* `service.local`.

Do not use the same domain for every scenario.

Device names can be described generically, such as:

* routers;
* clients;
* PCs;
* switches;
* local DNS server;
* root DNS server;
* authoritative DNS server;
* web server;
* main server.

The detailed prompt created later may assign exact device names.

## Output format

Generate at least 40 distinct lab scenarios.

For every scenario, use this exact structure:

### Scenario 01 — Short descriptive title

**Difficulty:** Easy, Medium or Advanced

**Main concepts:** comma-separated concepts

**Version A**

```text
Generate a detailed prompt file for this request: [complete natural-language lab request].

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: [the same complete natural-language lab request].

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

Repeat the structure for every scenario.

The body of Version A and Version B must remain identical except for the final directory-related instruction.

## Example

### Scenario 01 — Hierarchical DNS over IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, static routing, DNS hierarchy, web server, client

**Version A**

```text
Generate a detailed prompt file for this request: generate a lab composed of 5 routers with a maximum degree of 3. The network must use IPv4 and static routing, with all required routes defined manually. The lab must contain three DNS servers: a root DNS server, an authoritative DNS server for the org top-level domain and a local name server used by the client. Add a web server associated with the domain kathara.org and a client located in a different LAN. The client must be able to resolve kathara.org through the DNS hierarchy and reach the web server using its domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: generate a lab composed of 5 routers with a maximum degree of 3. The network must use IPv4 and static routing, with all required routes defined manually. The lab must contain three DNS servers: a root DNS server, an authoritative DNS server for the org top-level domain and a local name server used by the client. Add a web server associated with the domain kathara.org and a client located in a different LAN. The client must be able to resolve kathara.org through the DNS hierarchy and reach the web server using its domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

## Final checks

Before returning the result, verify that:

* at least 40 distinct scenarios have been generated;
* every scenario has exactly two versions;
* every Version A contains the required workspace instruction;
* every Version B contains the required Skill.md instruction;
* every version contains `Do not generate lab files in this step.`;
* the two versions of each scenario describe exactly the same lab;
* all prompts are written in natural language;
* no actual Kathara lab files, shell commands or configuration files have been generated;
* the scenarios contain a balanced selection of IPv4, IPv6 and dual-stack labs;
* the scenarios contain meaningful variations of routers, switches, PCs, servers, DNS and web services;
* only static routing is requested.
