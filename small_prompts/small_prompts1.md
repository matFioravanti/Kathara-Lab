# Kathara Lab Prompt Collection

> **45 distinct scenarios** — each with Version A and Version B.
> All scenarios request static routing only. No dynamic protocols.

---

### Scenario 01 — Two-Router IPv4 Static Routing Basics

**Difficulty:** Easy

**Main concepts:** IPv4, two routers, static routing, two LANs, PCs

**Version A**

```text
Generate a detailed prompt file for this request: design a simple Kathara lab with two routers connected by a point-to-point link. Each router must serve one LAN containing two PCs. The network must use IPv4 only. All routes must be configured statically. Each router must have an explicit route toward the remote LAN. The PCs on each LAN must be able to ping the PCs on the other LAN. No default routes are required because each router has only one remote network to reach.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a simple Kathara lab with two routers connected by a point-to-point link. Each router must serve one LAN containing two PCs. The network must use IPv4 only. All routes must be configured statically. Each router must have an explicit route toward the remote LAN. The PCs on each LAN must be able to ping the PCs on the other LAN. No default routes are required because each router has only one remote network to reach.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 02 — Three Routers in a Line, IPv4

**Difficulty:** Easy

**Main concepts:** IPv4, three routers, linear topology, static routing, three LANs

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with three routers arranged in a linear chain. Router R1 connects to router R2, and router R2 connects to router R3. Each router must serve a LAN with three PCs. The network must use IPv4 only. All routing tables must be configured with explicit static routes; default routes are not permitted on interior routers. The middle router R2 has a maximum degree of 2 router-to-router links. All nine PCs must be able to reach each other across the chain.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with three routers arranged in a linear chain. Router R1 connects to router R2, and router R2 connects to router R3. Each router must serve a LAN with three PCs. The network must use IPv4 only. All routing tables must be configured with explicit static routes; default routes are not permitted on interior routers. The middle router R2 has a maximum degree of 2 router-to-router links. All nine PCs must be able to reach each other across the chain.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 03 — Simple IPv6 Static Routing

**Difficulty:** Easy

**Main concepts:** IPv6, two routers, static routing, two LANs, PCs

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab using IPv6 exclusively. The lab must include two routers connected by a single point-to-point IPv6 link. Each router must serve one LAN containing three PCs. All IPv6 addresses must be assigned statically. Static routes must be configured manually on both routers so that PCs in each LAN can reach PCs in the other LAN. No dynamic routing protocols may be used. IPv4 must be disabled on all interfaces.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab using IPv6 exclusively. The lab must include two routers connected by a single point-to-point IPv6 link. Each router must serve one LAN containing three PCs. All IPv6 addresses must be assigned statically. Static routes must be configured manually on both routers so that PCs in each LAN can reach PCs in the other LAN. No dynamic routing protocols may be used. IPv4 must be disabled on all interfaces.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 04 — Four Routers in a Ring, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, ring topology, four routers, static routing, four LANs

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with four routers arranged in a ring topology. Each router connects to exactly two neighbouring routers. Each router also serves one LAN containing two PCs. The network uses IPv4 only. All routes must be explicitly defined as static routes. Each router must have complete routing tables so that every PC can reach every other PC. The maximum degree of any router, counting only router-to-router links, must not exceed 2. No default routes are permitted.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with four routers arranged in a ring topology. Each router connects to exactly two neighbouring routers. Each router also serves one LAN containing two PCs. The network uses IPv4 only. All routes must be explicitly defined as static routes. Each router must have complete routing tables so that every PC can reach every other PC. The maximum degree of any router, counting only router-to-router links, must not exceed 2. No default routes are permitted.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 05 — Star Topology with One Central Router, IPv4

**Difficulty:** Easy

**Main concepts:** IPv4, star topology, one central router, four LANs, static routing, default routes on edge nodes

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab where a single central router connects four separate LANs. Each LAN contains two PCs. The network uses IPv4. All routing is static. The central router must have explicit routes for each LAN on its directly connected interfaces. Each PC must use a static default route pointing to its local router interface. No additional routers are used; all four LANs attach directly to the one central router. All PCs must be able to reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab where a single central router connects four separate LANs. Each LAN contains two PCs. The network uses IPv4. All routing is static. The central router must have explicit routes for each LAN on its directly connected interfaces. Each PC must use a static default route pointing to its local router interface. No additional routers are used; all four LANs attach directly to the one central router. All PCs must be able to reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 06 — Tree Topology with Three Routers, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, tree topology, three routers, hierarchical routing, six LANs, static routing

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with a tree-shaped router topology. A root router connects to two child routers using point-to-point links. Each child router connects to one LAN with three PCs, and the root router also connects to its own LAN with two PCs. The network uses IPv4 only. All static routes must be explicitly defined. The child routers must use default routes pointing toward the root router. The root router must have explicit static routes for each child LAN. All PCs across the three LANs must reach each other.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with a tree-shaped router topology. A root router connects to two child routers using point-to-point links. Each child router connects to one LAN with three PCs, and the root router also connects to its own LAN with two PCs. The network uses IPv4 only. All static routes must be explicitly defined. The child routers must use default routes pointing toward the root router. The root router must have explicit static routes for each child LAN. All PCs across the three LANs must reach each other.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 07 — Dual-Stack IPv4 and IPv6 Static Routing

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, two routers, static routing, two LANs

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with two routers connected by a dual-stack point-to-point link that carries both IPv4 and IPv6 addresses. Each router must serve one LAN with two PCs. All devices must be configured with both IPv4 and IPv6 addresses. Static routes must be configured separately for both address families on each router. PCs must be able to reach each other using both IPv4 and IPv6. No dynamic routing or address autoconfiguration may be used; all addresses and routes are assigned statically.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with two routers connected by a dual-stack point-to-point link that carries both IPv4 and IPv6 addresses. Each router must serve one LAN with two PCs. All devices must be configured with both IPv4 and IPv6 addresses. Static routes must be configured separately for both address families on each router. PCs must be able to reach each other using both IPv4 and IPv6. No dynamic routing or address autoconfiguration may be used; all addresses and routes are assigned statically.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 08 — Ethernet Switch with Multiple Clients

**Difficulty:** Easy

**Main concepts:** Ethernet switch, one LAN, four clients, bridge, Layer 2

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with one Ethernet switch connecting four client machines on a single LAN. The switch operates at Layer 2 and connects all clients to the same broadcast domain. The clients must be assigned IPv4 addresses in the same subnet. No routers are needed. The lab must demonstrate that all four clients can communicate with each other through the switch. No routing configuration is required. The switch must be configured as a software bridge.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with one Ethernet switch connecting four client machines on a single LAN. The switch operates at Layer 2 and connects all clients to the same broadcast domain. The clients must be assigned IPv4 addresses in the same subnet. No routers are needed. The lab must demonstrate that all four clients can communicate with each other through the switch. No routing configuration is required. The switch must be configured as a software bridge.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 09 — One Switch per LAN, Two LANs, One Router

**Difficulty:** Easy

**Main concepts:** IPv4, Ethernet switches, one router, two LANs, static routing, multiple clients

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with two LANs, each containing one Ethernet switch and three clients. A single router connects the two LANs using one interface per LAN. The network uses IPv4 only. Static routes are configured on the router for both LANs. Each client uses a default route pointing to the router interface on its LAN. All six clients must be able to ping each other across the router. The switches operate at Layer 2 and require no routing configuration.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with two LANs, each containing one Ethernet switch and three clients. A single router connects the two LANs using one interface per LAN. The network uses IPv4 only. Static routes are configured on the router for both LANs. Each client uses a default route pointing to the router interface on its LAN. All six clients must be able to ping each other across the router. The switches operate at Layer 2 and require no routing configuration.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 10 — Central Web Server, IPv4, Three Routers

**Difficulty:** Medium

**Main concepts:** IPv4, web server, three routers, linear topology, static routing, clients

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with three routers arranged in a line. The leftmost router serves a LAN containing two clients. The rightmost router serves a LAN containing one web server running HTTP on port 80. The middle router has no end-user devices. The network uses IPv4 only. All routes must be manually configured as static routes. The clients must be able to reach the web server by IP address over HTTP. Default routes may be used on edge routers pointing toward the middle router.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with three routers arranged in a line. The leftmost router serves a LAN containing two clients. The rightmost router serves a LAN containing one web server running HTTP on port 80. The middle router has no end-user devices. The network uses IPv4 only. All routes must be manually configured as static routes. The clients must be able to reach the web server by IP address over HTTP. Default routes may be used on edge routers pointing toward the middle router.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 11 — Local DNS Server, IPv4, Two Routers

**Difficulty:** Medium

**Main concepts:** IPv4, local DNS server, two routers, static routing, client, web server, domain name resolution

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with two routers connected by a point-to-point IPv4 link. One router serves a LAN containing one client and one local DNS server. The other router serves a LAN containing one web server. The web server must be associated with the domain name example.net. The local DNS server must be configured as an authoritative server for example.net and must resolve the domain to the web server IP address. The client must use the local DNS server as its resolver and must be able to reach the web server using the domain name example.net. All routing must be static.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with two routers connected by a point-to-point IPv4 link. One router serves a LAN containing one client and one local DNS server. The other router serves a LAN containing one web server. The web server must be associated with the domain name example.net. The local DNS server must be configured as an authoritative server for example.net and must resolve the domain to the web server IP address. The client must use the local DNS server as its resolver and must be able to reach the web server using the domain name example.net. All routing must be static.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 12 — Hierarchical DNS over IPv4, Five Routers

**Difficulty:** Advanced

**Main concepts:** IPv4, hierarchical DNS, root DNS, TLD DNS, authoritative DNS, web server, static routing, five routers

**Version A**

```text
Generate a detailed prompt file for this request: generate a lab composed of 5 routers with a maximum degree of 3. The network must use IPv4 and static routing, with all required routes defined manually. The lab must contain three DNS servers: a root DNS server, an authoritative DNS server for the org top-level domain, and a local name server used by the client. Add a web server associated with the domain kathara.org and a client located in a different LAN. The client must be able to resolve kathara.org through the DNS hierarchy and reach the web server using its domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: generate a lab composed of 5 routers with a maximum degree of 3. The network must use IPv4 and static routing, with all required routes defined manually. The lab must contain three DNS servers: a root DNS server, an authoritative DNS server for the org top-level domain, and a local name server used by the client. Add a web server associated with the domain kathara.org and a client located in a different LAN. The client must be able to resolve kathara.org through the DNS hierarchy and reach the web server using its domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 13 — Main Server Reachable from All LANs, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, main server, four LANs, four routers, tree topology, static routing, clients

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with four routers arranged in a tree. A root router connects to three leaf routers using point-to-point links. Each leaf router serves a LAN with two PCs. The root router serves a LAN containing one main server that must be reachable from all other LANs. The network uses IPv4 only. All routing is static. Leaf routers must use default routes pointing toward the root. The root router must have explicit static routes to each leaf LAN. Every PC must be able to ping the main server.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with four routers arranged in a tree. A root router connects to three leaf routers using point-to-point links. Each leaf router serves a LAN with two PCs. The root router serves a LAN containing one main server that must be reachable from all other LANs. The network uses IPv4 only. All routing is static. Leaf routers must use default routes pointing toward the root. The root router must have explicit static routes to each leaf LAN. Every PC must be able to ping the main server.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 14 — IPv6-Only Ring Topology

**Difficulty:** Medium

**Main concepts:** IPv6, ring topology, four routers, static routing, four LANs, PCs

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab using IPv6 exclusively. The topology must be a ring of four routers, where each router connects to exactly two neighbouring routers. Each router must serve one LAN with two PCs. All IPv6 addresses must be assigned statically. Each router must have complete static IPv6 routing tables so that every PC can reach every other PC. No default routes may be used on any router. IPv4 must be disabled everywhere.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab using IPv6 exclusively. The topology must be a ring of four routers, where each router connects to exactly two neighbouring routers. Each router must serve one LAN with two PCs. All IPv6 addresses must be assigned statically. Each router must have complete static IPv6 routing tables so that every PC can reach every other PC. No default routes may be used on any router. IPv4 must be disabled everywhere.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 15 — Dual-Stack Tree Topology

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, tree topology, three routers, static routing, six LANs

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with a tree topology of three routers. A root router connects to two child routers over dual-stack point-to-point links. Each router serves one LAN. All routers, PCs, and the LAN interfaces must carry both IPv4 and IPv6 addresses. Routing tables must be configured statically for both address families. Each child router uses a static default route for both IPv4 and IPv6 pointing toward the root. The root must have explicit static routes for each child LAN in both address families. All PCs must be able to reach each other using either IPv4 or IPv6.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with a tree topology of three routers. A root router connects to two child routers over dual-stack point-to-point links. Each router serves one LAN. All routers, PCs, and the LAN interfaces must carry both IPv4 and IPv6 addresses. Routing tables must be configured statically for both address families. Each child router uses a static default route for both IPv4 and IPv6 pointing toward the root. The root must have explicit static routes for each child LAN in both address families. All PCs must be able to reach each other using either IPv4 or IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 16 — Two Web Servers, IPv4, Partial Mesh

**Difficulty:** Medium

**Main concepts:** IPv4, two web servers, partial mesh, four routers, static routing, clients

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with four routers in a partially meshed topology. Router R1 connects to R2 and R3. Router R2 connects to R4. Router R3 connects to R4. This forms a diamond shape. Router R1 serves a LAN with two clients. Router R2 serves a LAN with one web server for the domain network.lab. Router R3 serves a LAN with one web server for the domain service.local. Router R4 has no attached end-user devices. The network uses IPv4 only. All routing must be static. Clients must be able to reach both web servers by IP address.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with four routers in a partially meshed topology. Router R1 connects to R2 and R3. Router R2 connects to R4. Router R3 connects to R4. This forms a diamond shape. Router R1 serves a LAN with two clients. Router R2 serves a LAN with one web server for the domain network.lab. Router R3 serves a LAN with one web server for the domain service.local. Router R4 has no attached end-user devices. The network uses IPv4 only. All routing must be static. Clients must be able to reach both web servers by IP address.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 17 — Default Routes on Edge Routers, IPv4, Line Topology

**Difficulty:** Easy

**Main concepts:** IPv4, default routes, edge routers, line topology, four routers, static routing

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with four routers in a linear chain: R1-R2-R3-R4. Each router serves one LAN with two PCs. The network uses IPv4. The two edge routers R1 and R4 must use static default routes pointing toward their single router neighbour. The two interior routers R2 and R3 must have fully explicit routing tables without default routes, containing a specific static route for every remote LAN. All eight PCs must be able to reach each other.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with four routers in a linear chain: R1-R2-R3-R4. Each router serves one LAN with two PCs. The network uses IPv4. The two edge routers R1 and R4 must use static default routes pointing toward their single router neighbour. The two interior routers R2 and R3 must have fully explicit routing tables without default routes, containing a specific static route for every remote LAN. All eight PCs must be able to reach each other.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 18 — All Routes Explicit, No Default Routes, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, fully explicit routing tables, no default routes, five routers, partially meshed, static routing

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with five routers. Router R1 connects to R2 and R3. Router R2 connects to R4. Router R3 connects to R4. Router R4 connects to R5. Each router serves one LAN with two PCs. The network uses IPv4 only. Every router must have a fully explicit routing table with a specific static route for every remote subnet. Default routes must not appear on any router. All ten PCs must reach each other.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with five routers. Router R1 connects to R2 and R3. Router R2 connects to R4. Router R3 connects to R4. Router R4 connects to R5. Each router serves one LAN with two PCs. The network uses IPv4 only. Every router must have a fully explicit routing table with a specific static route for every remote subnet. Default routes must not appear on any router. All ten PCs must reach each other.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 19 — Max Router Degree 2, IPv4, Linear Chain

**Difficulty:** Easy

**Main concepts:** IPv4, maximum router degree 2, linear topology, three routers, static routing, PCs

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with three routers arranged in a line where the maximum router degree, counting only router-to-router links, must not exceed 2. Router R1 connects only to R2, and R2 connects only to R3. Each router serves one LAN with four PCs. The network uses IPv4 only. All routes are static. Edge routers may use default routes. The middle router must have explicit static routes for both remote LANs. All twelve PCs must reach each other.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with three routers arranged in a line where the maximum router degree, counting only router-to-router links, must not exceed 2. Router R1 connects only to R2, and R2 connects only to R3. Each router serves one LAN with four PCs. The network uses IPv4 only. All routes are static. Edge routers may use default routes. The middle router must have explicit static routes for both remote LANs. All twelve PCs must reach each other.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 20 — Max Router Degree 3, IPv4, Partial Mesh

**Difficulty:** Medium

**Main concepts:** IPv4, maximum router degree 3, partial mesh, six routers, static routing, clients

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with six routers where no router may have more than three router-to-router links. The topology must be partially meshed. Router R1 connects to R2, R3, and R4. Router R2 connects to R5. Router R3 connects to R5. Router R4 connects to R6. Router R5 connects to R6. Each router serves one LAN with two PCs. The network uses IPv4 only. All routes must be statically configured. All twelve PCs must reach each other.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with six routers where no router may have more than three router-to-router links. The topology must be partially meshed. Router R1 connects to R2, R3, and R4. Router R2 connects to R5. Router R3 connects to R5. Router R4 connects to R6. Router R5 connects to R6. Each router serves one LAN with two PCs. The network uses IPv4 only. All routes must be statically configured. All twelve PCs must reach each other.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 21 — Root, TLD, and Authoritative DNS, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, DNS hierarchy, root DNS, TLD DNS, authoritative DNS, web server, client, three routers, static routing

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with three routers in a linear chain. The leftmost router serves a LAN containing one client. The middle router serves a LAN containing a root DNS server and a top-level domain DNS server for the net zone. The rightmost router serves a LAN containing an authoritative DNS server for the domain research.org and a web server for that domain. The client must use the root DNS server as its resolver. The DNS hierarchy must allow the client to resolve research.org and reach the web server by name. The network uses IPv4. All routing must be static. Edge routers use default routes; the middle router has explicit static routes.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with three routers in a linear chain. The leftmost router serves a LAN containing one client. The middle router serves a LAN containing a root DNS server and a top-level domain DNS server for the net zone. The rightmost router serves a LAN containing an authoritative DNS server for the domain research.org and a web server for that domain. The client must use the root DNS server as its resolver. The DNS hierarchy must allow the client to resolve research.org and reach the web server by name. The network uses IPv4. All routing must be static. Edge routers use default routes; the middle router has explicit static routes.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 22 — Authoritative DNS for Multiple Domains, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, multiple authoritative DNS servers, two domains, two web servers, clients, static routing, four routers

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with four routers where R1 connects to R2, R2 connects to R3, and R3 connects to R4. Router R1 serves a LAN with two clients and one local DNS server. Router R2 serves a LAN with one authoritative DNS server for the domain university.edu and one web server for that domain. Router R3 serves a LAN with one authoritative DNS server for the domain company.test and one web server for that domain. Router R4 has no end-user devices. The local DNS server must forward queries for university.edu to its authoritative server and queries for company.test to its authoritative server. Clients must be able to resolve and reach both web servers by domain name. The network uses IPv4. All routing is static.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with four routers where R1 connects to R2, R2 connects to R3, and R3 connects to R4. Router R1 serves a LAN with two clients and one local DNS server. Router R2 serves a LAN with one authoritative DNS server for the domain university.edu and one web server for that domain. Router R3 serves a LAN with one authoritative DNS server for the domain company.test and one web server for that domain. Router R4 has no end-user devices. The local DNS server must forward queries for university.edu to its authoritative server and queries for company.test to its authoritative server. Clients must be able to resolve and reach both web servers by domain name. The network uses IPv4. All routing is static.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 23 — IPv6 Line Topology with Web Server

**Difficulty:** Medium

**Main concepts:** IPv6, three routers, linear topology, web server, client, static routing

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab that uses IPv6 exclusively. Three routers must be arranged in a line. The leftmost router serves a LAN with one client. The rightmost router serves a LAN with one web server running HTTP. The middle router has no attached end hosts. All IPv6 addresses and routes must be configured statically. Edge routers use IPv6 default routes. The middle router must have fully explicit IPv6 static routes. The client must be able to reach the web server by its IPv6 address over HTTP. No IPv4 configuration is needed anywhere.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab that uses IPv6 exclusively. Three routers must be arranged in a line. The leftmost router serves a LAN with one client. The rightmost router serves a LAN with one web server running HTTP. The middle router has no attached end hosts. All IPv6 addresses and routes must be configured statically. Edge routers use IPv6 default routes. The middle router must have fully explicit IPv6 static routes. The client must be able to reach the web server by its IPv6 address over HTTP. No IPv4 configuration is needed anywhere.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 24 — Dual-Stack with Central Main Server

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, central main server, four routers, star topology, static routing, clients

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with four routers in a star topology. A central router connects to three edge routers using dual-stack point-to-point links. Each edge router serves a LAN with two clients. The central router serves a LAN containing one main server. All devices must have both IPv4 and IPv6 addresses. All routes for both address families must be statically configured. Edge routers must use static default routes for both IPv4 and IPv6. The central router must have explicit static routes for each edge LAN in both address families. All clients must reach the main server using both IPv4 and IPv6.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with four routers in a star topology. A central router connects to three edge routers using dual-stack point-to-point links. Each edge router serves a LAN with two clients. The central router serves a LAN containing one main server. All devices must have both IPv4 and IPv6 addresses. All routes for both address families must be statically configured. Edge routers must use static default routes for both IPv4 and IPv6. The central router must have explicit static routes for each edge LAN in both address families. All clients must reach the main server using both IPv4 and IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 25 — Switch-Based LAN with Router Gateway, IPv4

**Difficulty:** Easy

**Main concepts:** IPv4, Ethernet switch, one router, two LANs, four clients per LAN, static routing

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with two LANs. Each LAN consists of one Ethernet switch connected to four clients and one router interface. The two routers are connected by a point-to-point IPv4 link. The network uses IPv4 only. Each client uses a static default route via its local router. The routers must have explicit static routes for the remote LAN. All eight clients must reach each other. The switches operate as Layer 2 bridges and require no IP configuration.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with two LANs. Each LAN consists of one Ethernet switch connected to four clients and one router interface. The two routers are connected by a point-to-point IPv4 link. The network uses IPv4 only. Each client uses a static default route via its local router. The routers must have explicit static routes for the remote LAN. All eight clients must reach each other. The switches operate as Layer 2 bridges and require no IP configuration.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 26 — Client Reaches Web Server by Name, IPv4, Simple DNS

**Difficulty:** Medium

**Main concepts:** IPv4, client, web server, authoritative DNS, domain name resolution, two routers, static routing

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with two routers connected by a point-to-point IPv4 link. One LAN contains one client and one authoritative DNS server for the domain service.local. The other LAN contains one web server associated with the domain service.local. The client must be configured to use the local DNS server as its resolver. The DNS server must be authoritative for service.local and must resolve the domain to the web server IP address. The client must be able to perform a DNS query, resolve service.local, and retrieve the web page using HTTP. All routes are static.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with two routers connected by a point-to-point IPv4 link. One LAN contains one client and one authoritative DNS server for the domain service.local. The other LAN contains one web server associated with the domain service.local. The client must be configured to use the local DNS server as its resolver. The DNS server must be authoritative for service.local and must resolve the domain to the web server IP address. The client must be able to perform a DNS query, resolve service.local, and retrieve the web page using HTTP. All routes are static.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 27 — Five-Router Partial Mesh, All Explicit Routes, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, partial mesh, five routers, maximum degree 3, fully explicit static routes, no default routes

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with five routers in a partial mesh. Router R1 connects to R2 and R3. Router R2 connects to R4. Router R3 connects to R4 and R5. Router R4 connects to R5. No router may have more than three router-to-router links. Each router serves one LAN with two PCs. The network uses IPv4 only. All routers must have fully explicit static routing tables. Default routes are not allowed. All ten PCs must reach each other. Verify that no router degree exceeds 3.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with five routers in a partial mesh. Router R1 connects to R2 and R3. Router R2 connects to R4. Router R3 connects to R4 and R5. Router R4 connects to R5. No router may have more than three router-to-router links. Each router serves one LAN with two PCs. The network uses IPv4 only. All routers must have fully explicit static routing tables. Default routes are not allowed. All ten PCs must reach each other. Verify that no router degree exceeds 3.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 28 — IPv6 Tree with Local DNS and Web Server

**Difficulty:** Advanced

**Main concepts:** IPv6, tree topology, three routers, local DNS server, authoritative DNS, web server, client, static routing

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab using IPv6 exclusively. The topology is a tree with one root router connected to two leaf routers. The root router serves a LAN containing one client and one local DNS server. The first leaf router serves a LAN with one web server for the domain network.lab. The second leaf router serves a LAN with one authoritative DNS server for the domain network.lab. The local DNS server must be configured to forward queries for network.lab to the authoritative server. The client must resolve network.lab using the local DNS server and reach the web server by name using IPv6. All addresses and routes are static.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab using IPv6 exclusively. The topology is a tree with one root router connected to two leaf routers. The root router serves a LAN containing one client and one local DNS server. The first leaf router serves a LAN with one web server for the domain network.lab. The second leaf router serves a LAN with one authoritative DNS server for the domain network.lab. The local DNS server must be configured to forward queries for network.lab to the authoritative server. The client must resolve network.lab using the local DNS server and reach the web server by name using IPv6. All addresses and routes are static.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 29 — Main Server Plus DNS, IPv4, Star Topology

**Difficulty:** Advanced

**Main concepts:** IPv4, star topology, main server, DNS, client, three routers, static routing, domain name resolution

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with a star topology. A central router connects to three edge routers. The first edge LAN contains two clients and one local DNS server. The second edge LAN contains one main server that serves files over HTTP and is reachable at the domain main.example.net. The third edge LAN contains one authoritative DNS server for example.net. The local DNS server must resolve example.net by delegating to the authoritative server. The clients must reach the main server by domain name. All routing is IPv4 and static. The central router must have explicit routes to all three edge LANs. Edge routers use default routes.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with a star topology. A central router connects to three edge routers. The first edge LAN contains two clients and one local DNS server. The second edge LAN contains one main server that serves files over HTTP and is reachable at the domain main.example.net. The third edge LAN contains one authoritative DNS server for example.net. The local DNS server must resolve example.net by delegating to the authoritative server. The clients must reach the main server by domain name. All routing is IPv4 and static. The central router must have explicit routes to all three edge LANs. Edge routers use default routes.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 30 — Dual-Stack Line Topology, Three Routers

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, three routers, linear topology, static routing, PCs

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with three routers in a linear chain. All inter-router links must carry both IPv4 and IPv6 addresses. Each router serves one LAN with three PCs. PCs in each LAN must also have both IPv4 and IPv6 addresses. All routes for both address families must be configured statically. The two edge routers use static default routes for both IPv4 and IPv6. The middle router must have explicit static routes for both edge LANs in both address families. All nine PCs must reach each other using either protocol.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with three routers in a linear chain. All inter-router links must carry both IPv4 and IPv6 addresses. Each router serves one LAN with three PCs. PCs in each LAN must also have both IPv4 and IPv6 addresses. All routes for both address families must be configured statically. The two edge routers use static default routes for both IPv4 and IPv6. The middle router must have explicit static routes for both edge LANs in both address families. All nine PCs must reach each other using either protocol.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 31 — Large Star with Five Leaf Routers, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, star topology, six routers, five LANs, static routing, default routes, many PCs

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab where one central router connects to five leaf routers using point-to-point IPv4 links. Each leaf router serves a LAN with three PCs. The central router does not serve a LAN of its own. The network uses IPv4 only. All leaf routers must use a static default route pointing toward the central router. The central router must have explicit static routes for all five leaf LANs. All fifteen PCs must be able to reach each other. The maximum router degree of the central router is 5.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab where one central router connects to five leaf routers using point-to-point IPv4 links. Each leaf router serves a LAN with three PCs. The central router does not serve a LAN of its own. The network uses IPv4 only. All leaf routers must use a static default route pointing toward the central router. The central router must have explicit static routes for all five leaf LANs. All fifteen PCs must be able to reach each other. The maximum router degree of the central router is 5.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 32 — IPv4 Lab with One Switch and One Router

**Difficulty:** Easy

**Main concepts:** IPv4, Ethernet switch, one router, two LANs, clients, static routing

**Version A**

```text
Generate a detailed prompt file for this request: build a simple Kathara lab with one router and one Ethernet switch. The router has two interfaces: one connects directly to three PCs in a first LAN, and the other connects to the Ethernet switch. The switch serves a second LAN containing four clients. The network uses IPv4. Each client and PC uses a default route via the router. The router is directly connected to both subnets and requires no additional static routes. All seven devices must reach each other.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a simple Kathara lab with one router and one Ethernet switch. The router has two interfaces: one connects directly to three PCs in a first LAN, and the other connects to the Ethernet switch. The switch serves a second LAN containing four clients. The network uses IPv4. Each client and PC uses a default route via the router. The router is directly connected to both subnets and requires no additional static routes. All seven devices must reach each other.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 33 — Root DNS, TLD DNS, Two Authoritative DNS Servers

**Difficulty:** Advanced

**Main concepts:** IPv4, DNS hierarchy, root DNS, TLD DNS, two authoritative DNS servers, two web servers, five routers

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with five routers. R1 connects to R2 and R3. R2 connects to R4. R3 connects to R5. Each router serves a dedicated LAN. The LAN on R1 contains one client configured to use the root DNS server as its resolver. The LAN on R2 contains the root DNS server and the top-level domain DNS server for the edu zone. The LAN on R3 contains an authoritative DNS server for university.edu and a web server for that domain. The LAN on R4 contains an authoritative DNS server for research.edu and a web server for that domain. The LAN on R5 has two extra PCs. The client must be able to resolve and contact both university.edu and research.edu web servers by name. The network uses IPv4. All routing is static. No default routes are used on any router.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with five routers. R1 connects to R2 and R3. R2 connects to R4. R3 connects to R5. Each router serves a dedicated LAN. The LAN on R1 contains one client configured to use the root DNS server as its resolver. The LAN on R2 contains the root DNS server and the top-level domain DNS server for the edu zone. The LAN on R3 contains an authoritative DNS server for university.edu and a web server for that domain. The LAN on R4 contains an authoritative DNS server for research.edu and a web server for that domain. The LAN on R5 has two extra PCs. The client must be able to resolve and contact both university.edu and research.edu web servers by name. The network uses IPv4. All routing is static. No default routes are used on any router.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 34 — IPv6 Star with Web Server and Clients

**Difficulty:** Medium

**Main concepts:** IPv6, star topology, three routers, web server, clients, static routing

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab using IPv6 only. One central router connects to two edge routers. The first edge router serves a LAN with three clients. The second edge router serves a LAN with one web server. All addresses are assigned statically using IPv6. Edge routers use IPv6 default routes toward the central router. The central router has explicit static IPv6 routes for both edge LANs. The clients must reach the web server by its IPv6 address using HTTP. No IPv4 configuration is required.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab using IPv6 only. One central router connects to two edge routers. The first edge router serves a LAN with three clients. The second edge router serves a LAN with one web server. All addresses are assigned statically using IPv6. Edge routers use IPv6 default routes toward the central router. The central router has explicit static IPv6 routes for both edge LANs. The clients must reach the web server by its IPv6 address using HTTP. No IPv4 configuration is required.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 35 — Dual-Stack Partial Mesh, Three Routers, DNS

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, partial mesh, three routers, DNS, web server, client

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab where three routers form a partial mesh: R1 connects to R2 and R3, and R2 connects to R3. Each router serves one LAN. All inter-router links are dual-stack. Router R1 serves a LAN with one client and one local DNS server. Router R2 serves a LAN with one web server for the domain company.test. Router R3 has two PCs. The local DNS server must resolve company.test and provide both its IPv4 and IPv6 addresses to the client. The client must reach the web server using both IPv4 and IPv6 by name. All addresses and routes are configured statically for both address families.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab where three routers form a partial mesh: R1 connects to R2 and R3, and R2 connects to R3. Each router serves one LAN. All inter-router links are dual-stack. Router R1 serves a LAN with one client and one local DNS server. Router R2 serves a LAN with one web server for the domain company.test. Router R3 has two PCs. The local DNS server must resolve company.test and provide both its IPv4 and IPv6 addresses to the client. The client must reach the web server using both IPv4 and IPv6 by name. All addresses and routes are configured statically for both address families.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 36 — Multiple Web Servers, Hierarchical Routing, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, multiple web servers, hierarchical routing, six routers, tree topology, static routing, clients

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with six routers arranged in a two-level tree. A root router connects to two intermediate routers. Each intermediate router connects to two leaf routers. Each leaf router serves a LAN with one web server and one client. The root router has no attached end hosts. The network uses IPv4 only. All routing is static. Leaf routers use default routes toward their intermediate router. Intermediate routers use default routes toward the root. The root router has explicit static routes for all four leaf LANs. Every client must reach every web server.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with six routers arranged in a two-level tree. A root router connects to two intermediate routers. Each intermediate router connects to two leaf routers. Each leaf router serves a LAN with one web server and one client. The root router has no attached end hosts. The network uses IPv4 only. All routing is static. Leaf routers use default routes toward their intermediate router. Intermediate routers use default routes toward the root. The root router has explicit static routes for all four leaf LANs. Every client must reach every web server.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 37 — Six-Router Ring, IPv4, All Explicit Routes

**Difficulty:** Advanced

**Main concepts:** IPv4, ring topology, six routers, fully explicit static routes, no default routes, six LANs

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with six routers arranged in a ring. Each router connects to exactly two neighbouring routers. Each router serves one LAN with two PCs. The network uses IPv4 only. Every router must have fully explicit static routes for all remote LANs and all point-to-point inter-router links. Default routes must not appear on any router. The maximum router degree, counting only router-to-router links, must be exactly 2. All twelve PCs must reach each other.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with six routers arranged in a ring. Each router connects to exactly two neighbouring routers. Each router serves one LAN with two PCs. The network uses IPv4 only. Every router must have fully explicit static routes for all remote LANs and all point-to-point inter-router links. Default routes must not appear on any router. The maximum router degree, counting only router-to-router links, must be exactly 2. All twelve PCs must reach each other.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 38 — IPv4 Lab with Switch, Router, DNS, and Web Server

**Difficulty:** Medium

**Main concepts:** IPv4, Ethernet switch, router, local DNS, web server, client, domain name resolution

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with one router and one Ethernet switch. The first LAN, connected directly to the router, contains one web server for the domain kathara.org. The second LAN, served through the Ethernet switch, contains two clients and one authoritative DNS server for kathara.org. The router connects the two LANs using IPv4. All routes are static; the router is directly connected to both subnets. Clients must use the DNS server to resolve kathara.org and access the web server by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with one router and one Ethernet switch. The first LAN, connected directly to the router, contains one web server for the domain kathara.org. The second LAN, served through the Ethernet switch, contains two clients and one authoritative DNS server for kathara.org. The router connects the two LANs using IPv4. All routes are static; the router is directly connected to both subnets. Clients must use the DNS server to resolve kathara.org and access the web server by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 39 — Dual-Stack Ring, Four Routers, PCs

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, ring topology, four routers, static routing, no default routes

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with four routers in a ring topology. All inter-router links must be dual-stack, carrying both IPv4 and IPv6 addresses. Each router serves one LAN with two PCs that are also dual-stack. All routes for both IPv4 and IPv6 must be explicitly configured as static routes. Default routes are not permitted. All eight PCs must reach each other using both IPv4 and IPv6. The maximum router degree is 2 in terms of router-to-router links.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with four routers in a ring topology. All inter-router links must be dual-stack, carrying both IPv4 and IPv6 addresses. Each router serves one LAN with two PCs that are also dual-stack. All routes for both IPv4 and IPv6 must be explicitly configured as static routes. Default routes are not permitted. All eight PCs must reach each other using both IPv4 and IPv6. The maximum router degree is 2 in terms of router-to-router links.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 40 — Complete Routing, DNS, and Web Lab, IPv4, Six Routers

**Difficulty:** Advanced

**Main concepts:** IPv4, six routers, partial mesh, static routing, root DNS, TLD DNS, authoritative DNS, local DNS, web server, main server, client

**Version A**

```text
Generate a detailed prompt file for this request: create a comprehensive Kathara lab with six routers. The topology is partially meshed: R1 connects to R2 and R3; R2 connects to R4 and R5; R3 connects to R5; R4 connects to R6; R5 connects to R6. No router may have more than 3 router-to-router links. Each router serves one LAN. The LAN on R1 contains one client and one local DNS server. The LAN on R2 contains a root DNS server. The LAN on R3 contains a top-level domain DNS server for the org zone. The LAN on R4 contains an authoritative DNS server for research.org and a web server for that domain. The LAN on R5 contains a main server reachable at main.research.org. The LAN on R6 contains two additional PCs. The client must resolve research.org and main.research.org through the full DNS hierarchy and reach both servers by name. All routing is IPv4 and static with fully explicit routing tables on all routers.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a comprehensive Kathara lab with six routers. The topology is partially meshed: R1 connects to R2 and R3; R2 connects to R4 and R5; R3 connects to R5; R4 connects to R6; R5 connects to R6. No router may have more than 3 router-to-router links. Each router serves one LAN. The LAN on R1 contains one client and one local DNS server. The LAN on R2 contains a root DNS server. The LAN on R3 contains a top-level domain DNS server for the org zone. The LAN on R4 contains an authoritative DNS server for research.org and a web server for that domain. The LAN on R5 contains a main server reachable at main.research.org. The LAN on R6 contains two additional PCs. The client must resolve research.org and main.research.org through the full DNS hierarchy and reach both servers by name. All routing is IPv4 and static with fully explicit routing tables on all routers.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 41 — IPv4 Subnetting with One Router and Four LANs

**Difficulty:** Easy

**Main concepts:** IPv4, subnetting, one router, four LANs, four PCs, default routes on PCs

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab that demonstrates IPv4 subnetting. A single router must connect four LANs on four separate interfaces. Each LAN contains one PC. All four LANs must be subnets carved from the same address block. The router is directly connected to all subnets and requires no additional static routes. Each PC must use a static default route pointing to its local router interface. All four PCs must reach each other through the router.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab that demonstrates IPv4 subnetting. A single router must connect four LANs on four separate interfaces. Each LAN contains one PC. All four LANs must be subnets carved from the same address block. The router is directly connected to all subnets and requires no additional static routes. Each PC must use a static default route pointing to its local router interface. All four PCs must reach each other through the router.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 42 — IPv6 Partial Mesh, Five Routers, All Explicit Routes

**Difficulty:** Advanced

**Main concepts:** IPv6, partial mesh, five routers, fully explicit static routes, no default routes, PCs

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab that uses IPv6 exclusively. Five routers form a partial mesh: R1 connects to R2 and R3; R2 connects to R4; R3 connects to R4; R4 connects to R5. Each router serves one LAN with two PCs. All IPv6 addresses and routes must be configured statically. Every router must have a fully explicit IPv6 routing table with a specific static route for every remote subnet. Default routes are not permitted. IPv4 must be disabled everywhere. All ten PCs must reach each other.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab that uses IPv6 exclusively. Five routers form a partial mesh: R1 connects to R2 and R3; R2 connects to R4; R3 connects to R4; R4 connects to R5. Each router serves one LAN with two PCs. All IPv6 addresses and routes must be configured statically. Every router must have a fully explicit IPv6 routing table with a specific static route for every remote subnet. Default routes are not permitted. IPv4 must be disabled everywhere. All ten PCs must reach each other.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 43 — Three Switches, One Router, IPv4, Many Clients

**Difficulty:** Medium

**Main concepts:** IPv4, three Ethernet switches, one router, three LANs, many clients, static routing

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with one router connected to three Ethernet switches, one switch per LAN. Each switch connects five clients to its LAN segment. The router uses one interface per LAN and is directly connected to all three subnets. The network uses IPv4. Clients use a static default route via the local router interface. The router requires no additional static routes as it is directly attached to all subnets. All fifteen clients must be able to reach each other across all three LANs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with one router connected to three Ethernet switches, one switch per LAN. Each switch connects five clients to its LAN segment. The router uses one interface per LAN and is directly connected to all three subnets. The network uses IPv4. Clients use a static default route via the local router interface. The router requires no additional static routes as it is directly attached to all subnets. All fifteen clients must be able to reach each other across all three LANs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 44 — Dual-Stack Partial Mesh, DNS and Web, Six Routers

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, partial mesh, six routers, hierarchical DNS, web server, client

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with six routers in a partial mesh. R1 connects to R2 and R3. R2 connects to R4. R3 connects to R4 and R5. R4 connects to R6. R5 connects to R6. All inter-router links must be dual-stack. Router R1 serves a dual-stack LAN with one client and one local DNS server. Router R3 serves a dual-stack LAN with a root DNS server. Router R4 serves a dual-stack LAN with an authoritative DNS server for the domain example.net and a web server for that domain. Remaining routers serve dual-stack LANs with two PCs each. The local DNS server must forward queries and eventually resolve example.net using the DNS hierarchy. The client must reach the web server for example.net by name using both IPv4 and IPv6. All addresses and routes for both address families are configured statically.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with six routers in a partial mesh. R1 connects to R2 and R3. R2 connects to R4. R3 connects to R4 and R5. R4 connects to R6. R5 connects to R6. All inter-router links must be dual-stack. Router R1 serves a dual-stack LAN with one client and one local DNS server. Router R3 serves a dual-stack LAN with a root DNS server. Router R4 serves a dual-stack LAN with an authoritative DNS server for the domain example.net and a web server for that domain. Remaining routers serve dual-stack LANs with two PCs each. The local DNS server must forward queries and eventually resolve example.net using the DNS hierarchy. The client must reach the web server for example.net by name using both IPv4 and IPv6. All addresses and routes for both address families are configured statically.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 45 — Selective Connectivity: Client Reaches Only One of Two Servers

**Difficulty:** Medium

**Main concepts:** IPv4, selective routing, two web servers, three routers, static routing, restricted access

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with three routers. R1 connects to R2 and R3. R2 serves a LAN containing one client and one local DNS server. R1 serves a LAN containing web server A for the domain server-a.example.net. R3 serves a LAN containing web server B for the domain server-b.example.net. The client's static routing must be configured so that it can reach web server A but has no route to reach web server B. The local DNS server is authoritative for both domains. The routing tables must make web server B unreachable from the client while web server A remains fully accessible. All routing is IPv4 and static. Demonstrate the selective reachability requirement explicitly in the routing table design.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with three routers. R1 connects to R2 and R3. R2 serves a LAN containing one client and one local DNS server. R1 serves a LAN containing web server A for the domain server-a.example.net. R3 serves a LAN containing web server B for the domain server-b.example.net. The client's static routing must be configured so that it can reach web server A but has no route to reach web server B. The local DNS server is authoritative for both domains. The routing tables must make web server B unreachable from the client while web server A remains fully accessible. All routing is IPv4 and static. Demonstrate the selective reachability requirement explicitly in the routing table design.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

## Coverage Summary

| Category | Scenarios |
|---|---|
| Simple IPv4 static routing | 01, 02, 19, 41 |
| Simple IPv6 static routing | 03, 23, 34 |
| Dual-stack IPv4/IPv6 | 07, 15, 24, 30, 35, 39, 44 |
| One router, multiple LANs | 05, 32, 43 |
| Routers in a line | 02, 10, 17, 30 |
| Routers in a tree | 06, 13, 15, 36 |
| Routers in a ring | 04, 14, 37, 39 |
| Partial mesh topology | 16, 18, 20, 27, 35, 44 |
| Ethernet switches | 08, 09, 25, 32, 38, 43 |
| One central web server | 10, 26 |
| Multiple web servers | 16, 22, 33, 36 |
| Local DNS server | 11, 26, 38 |
| Root + TLD + local DNS | 21, 33 |
| Authoritative DNS multiple domains | 22, 33 |
| Client reaches server by name | 11, 21, 26, 28, 29, 38 |
| Main/central server | 13, 24, 29, 40 |
| Default routes on edge routers | 06, 07, 10, 13, 17, 31, 36 |
| All routes explicit, no defaults | 04, 14, 18, 27, 37, 42 |
| Maximum degree constraints | 04, 19, 20, 27, 37, 40 |
| Routing + DNS + web combined | 12, 28, 29, 33, 35, 40, 44 |
