# Generate Simple Natural-Language Prompts for Kathara Labs

You are responsible for creating a large collection of small prompts for Kathara networking labs.

Your task is **not** to create the labs.

Your task is only to write the small prompts that will later be given to another AI agent. That agent will use each small prompt to prepare a detailed lab specification.

## Reference Material

Before writing the prompts, inspect all files and folders inside:

```text
kathara-lab-exercises
```

Use these files only as examples to understand:

- common Kathara lab topologies;
- how routers, switches, PCs, clients and servers can be combined;
- simple, medium and advanced lab sizes;
- IPv4, IPv6 and dual-stack labs;
- static routing;
- manually written routing tables;
- default routes;
- DNS labs;
- web server labs;
- central server labs;
- realistic connectivity goals;
- the style of existing lab requests.

Do not copy an existing exercise word for word.

Create new lab ideas inspired by the examples.

## Main Goal

Generate many short prompts that describe different Kathara labs.

The prompts must use simple and natural English.

They should sound like a person explaining what kind of lab they want.

Do not write them like formal technical documents.

Do not use complicated wording when a simpler sentence says the same thing.

## Simple Language Rules

Every generated mini-prompt must:

- use clear everyday English;
- use short and direct sentences;
- use natural language;
- avoid long or complicated sentence structures;
- avoid unnecessary technical jargon;
- use technical words only when they are needed;
- describe the lab in one compact paragraph;
- explain what devices are needed;
- explain the main network structure;
- explain which services are needed;
- explain what must work at the end;
- avoid giving the complete solution.

Use normal technical words such as:

- router;
- switch;
- PC;
- client;
- server;
- IPv4;
- IPv6;
- static routing;
- default route;
- DNS server;
- web server;
- root DNS server;
- local DNS server;
- authoritative DNS server.

Avoid overly formal expressions such as:

- implementation-ready specification;
- end-to-end validation objective;
- hierarchical resolution workflow;
- manually provisioned forwarding information;
- service placement constraints;
- topology compliance requirements;
- deterministic addressing architecture.

Use simpler expressions instead.

For example:

Too formal:

```text
The scenario must implement a hierarchical DNS resolution workflow across multiple routed network segments.
```

Better:

```text
The client must use the DNS servers to find the web server by name, even though the servers are in different networks.
```

Too formal:

```text
All forwarding information must be statically provisioned on every routing device.
```

Better:

```text
Configure all router routes manually. Do not use dynamic routing.
```

Too formal:

```text
The topology must satisfy a maximum router-degree constraint of three.
```

Better:

```text
No router can be connected to more than three other networks or routers.
```

## Allowed Lab Elements

The prompts may include different combinations of:

- PCs;
- clients;
- routers;
- Ethernet switches;
- IPv4 networks;
- IPv6 networks;
- dual-stack networks;
- static routes;
- complete static routing tables;
- default routes;
- web servers;
- central servers;
- DNS servers;
- local DNS servers;
- root DNS servers;
- top-level domain DNS servers;
- authoritative DNS servers;
- clients that contact servers by domain name.

Only request static network configurations.

Do not request dynamic routing protocols such as:

- RIP;
- RIPng;
- OSPF;
- OSPFv3;
- BGP;
- IS-IS.

## Prompt Pairs

For every lab scenario, create exactly two versions of the same mini-prompt.

The lab request in Version A and Version B must be identical.

Only the final directory instruction must change.

### Version A

Version A must end with these exact sentences:

```text
Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

### Version B

Version B must end with these exact sentences:

```text
Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

Do not put both directory instructions in the same version.

## Mini-Prompt Requirements

Every mini-prompt must:

- be written in English;
- be self-contained;
- use simple natural language;
- be easy to understand;
- be short but complete;
- contain no source code;
- contain no `lab.conf` content;
- contain no `.startup` file content;
- contain no shell commands;
- avoid giving a complete IP plan unless fixed addresses are part of the request;
- describe the topology, services and expected connectivity;
- ask for a detailed prompt file;
- not ask the other AI to create the actual lab files yet.

Each mini-prompt must start with:

```text
Generate a detailed prompt file for this request:
```

After this sentence, describe the lab in simple natural language.

## Information That May Be Included

A mini-prompt may include:

- how many routers are needed;
- how many switches are needed;
- how many PCs or clients are needed;
- how many servers are needed;
- the role of each server;
- how many LANs are needed;
- whether router links form a line, tree, ring, star or partial mesh;
- whether a router has a maximum number of connections;
- whether the lab uses IPv4, IPv6 or both;
- whether all routes must be written manually;
- whether default routes are allowed;
- whether edge routers should use default routes;
- whether each router needs a complete routing table;
- which clients must reach which servers;
- whether all clients must reach every network;
- the DNS server structure;
- the domain name used by a server;
- whether a client must reach a web server by name;
- whether a central server must be reachable from every LAN;
- whether redundant physical paths are allowed.

Do not explain how to configure these things.

Only describe what the final lab must contain and what must work.

## Variety Requirements

Generate at least 40 different lab scenarios.

Include easy, medium and advanced labs.

The collection must include examples from all of these groups:

1. Simple IPv4 labs with static routing.
2. Simple IPv6 labs with static routing.
3. Dual-stack labs.
4. One router connecting several LANs.
5. Several routers connected in a line.
6. Routers connected as a tree.
7. Routers connected as a ring.
8. Routers connected in a partial mesh.
9. Switches with several PCs.
10. One central web server.
11. More than one web server.
12. One local DNS server.
13. A root DNS server, a top-level domain DNS server and a local DNS server.
14. Authoritative DNS servers for different domains.
15. A client reaching a web server by domain name.
16. A central server reachable from all LANs.
17. Edge routers using static default routes.
18. Labs where every route is written explicitly.
19. Labs with limits on the number of router connections.
20. Labs that combine routing, DNS and web services.

Do not create many prompts that are almost the same.

Changing only the number of routers or clients is not enough.

Each scenario should change something important, such as:

- the topology;
- the IP version;
- the routing rules;
- the server position;
- the DNS structure;
- the allowed connectivity;
- the use of default routes;
- the difficulty.

## Technical Checks

Before writing each mini-prompt, make sure the requested lab is possible.

Check that:

- every LAN can be connected to a router;
- the requested router connections are possible;
- maximum router connection limits make sense;
- every required client has a path to the required server;
- static routing is enough;
- clients can reach their DNS server;
- DNS servers can reach the other DNS servers they need;
- the chosen domain name matches the correct server;
- an IPv4-only client is not asked to reach an IPv6-only service;
- an IPv6-only client is not asked to reach an IPv4-only service;
- the scenario does not need a dynamic routing protocol.

Do not solve the lab inside the mini-prompt.

Only describe the requirements.

## Names

Use different fictional domain names and server names.

Examples include:

- `kathara.org`;
- `example.net`;
- `network.lab`;
- `university.edu`;
- `company.test`;
- `research.org`;
- `service.local`;
- `campus.net`;
- `library.test`;
- `training.lab`.

Do not use the same domain name in every scenario.

Device names can remain simple and generic, such as:

- router;
- client;
- PC;
- switch;
- local DNS server;
- root DNS server;
- authoritative DNS server;
- web server;
- central server.

The detailed prompt created later can choose exact device names.

## Output Format

Use this exact structure for every scenario:

### Scenario 01 — Short descriptive title

**Difficulty:** Easy, Medium or Advanced

**Main concepts:** comma-separated concepts

**Version A**

```text
Generate a detailed prompt file for this request: [simple natural-language description of the requested lab].

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: [the exact same simple natural-language description].

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

Repeat this structure for every scenario.

The lab description in Version A and Version B must be exactly the same.

## Example

### Scenario 01 — DNS and Web Server Across Several Networks

**Difficulty:** Advanced

**Main concepts:** IPv4, static routing, DNS, web server, client

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with five routers. No router should connect to more than three other routers or networks. Use IPv4 and configure all routes manually. Add a root DNS server, a DNS server for the org domain and a local DNS server used by the client. Add a web server for kathara.org and place the client in another LAN. The client must be able to find kathara.org through DNS and open the web server by using its domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with five routers. No router should connect to more than three other routers or networks. Use IPv4 and configure all routes manually. Add a root DNS server, a DNS server for the org domain and a local DNS server used by the client. Add a web server for kathara.org and place the client in another LAN. The client must be able to find kathara.org through DNS and open the web server by using its domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

## Final Checks

Before returning the result, verify that:

- at least 40 different scenarios were created;
- every scenario has exactly two versions;
- every Version A contains the required workspace instruction;
- every Version B contains the required Skill.md instruction;
- every version contains `Do not generate lab files in this step.`;
- Version A and Version B describe exactly the same lab;
- all mini-prompts use simple natural English;
- the mini-prompts sound like normal requests, not formal specifications;
- no lab files, configuration files, source code or shell commands were generated;
- IPv4, IPv6 and dual-stack labs are all included;
- routers, switches, PCs, DNS servers and web servers are used in meaningful combinations;
- only static routing is requested;
- the prompts describe requirements without giving the solution.
