# Kathara Lab Prompt Collection — Set 2

> **40 distinct scenarios** — Medium and Advanced only.
> Each with Version A and Version B.
> All scenarios request static routing only. No dynamic protocols.
> All scenarios are different from the ones in small_prompts1.md.

---

### Scenario 01 — Dual-Stack Diamond Topology with Four Routers

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, diamond topology, four routers, static routing

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with four routers arranged in a diamond shape. One router at the top connects to two middle routers, and both middle routers connect to one router at the bottom. Each router serves one LAN with two PCs. The network must use both IPv4 and IPv6 on all devices. All routes must be configured statically for both address families. Every PC must be able to reach every other PC using both IPv4 and IPv6. No default routes are allowed.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with four routers arranged in a diamond shape. One router at the top connects to two middle routers, and both middle routers connect to one router at the bottom. Each router serves one LAN with two PCs. The network must use both IPv4 and IPv6 on all devices. All routes must be configured statically for both address families. Every PC must be able to reach every other PC using both IPv4 and IPv6. No default routes are allowed.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 02 — IPv4 Partial Mesh with Redundant Paths and Web Server

**Difficulty:** Advanced

**Main concepts:** IPv4, partial mesh, redundant paths, four routers, web server, static routing

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with four routers connected in a partial mesh where at least two different physical paths exist between any pair of routers. Each router has a maximum degree of 3. One router serves a LAN with a web server. Two other routers each serve a LAN with two clients. The fourth router acts as a transit router with no LAN. Use IPv4. All routes must be configured manually. Each client must reach the web server by its IP address. Configure routing so that traffic uses consistent paths even though redundant links exist.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with four routers connected in a partial mesh where at least two different physical paths exist between any pair of routers. Each router has a maximum degree of 3. One router serves a LAN with a web server. Two other routers each serve a LAN with two clients. The fourth router acts as a transit router with no LAN. Use IPv4. All routes must be configured manually. Each client must reach the web server by its IP address. Configure routing so that traffic uses consistent paths even though redundant links exist.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 03 — IPv6 Five-Router Line with DNS and Web Server

**Difficulty:** Advanced

**Main concepts:** IPv6, linear topology, five routers, local DNS server, web server, static routing

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab using IPv6 only. Arrange five routers in a line. The first router connects to a LAN with a client and a local DNS server. The last router connects to a LAN with a web server for the domain network.lab. The three middle routers are transit routers without LANs. Write all IPv6 routes by hand on every router. The client must resolve network.lab through the local DNS server and then access the web server by domain name. No default routes are allowed on interior routers. Edge routers may use a default route.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab using IPv6 only. Arrange five routers in a line. The first router connects to a LAN with a client and a local DNS server. The last router connects to a LAN with a web server for the domain network.lab. The three middle routers are transit routers without LANs. Write all IPv6 routes by hand on every router. The client must resolve network.lab through the local DNS server and then access the web server by domain name. No default routes are allowed on interior routers. Edge routers may use a default route.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 04 — IPv4 Hub-and-Spoke with Two Central Routers

**Difficulty:** Medium

**Main concepts:** IPv4, hub-and-spoke, two central routers, six LANs, static routing, default routes

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with two central routers connected to each other. Each central router connects to two edge routers. Each edge router serves one LAN with three PCs. The two central routers do not serve any LAN directly. Use IPv4. Edge routers must use a default route pointing to their central router. The central routers must have explicit routes to all four edge LANs and to each other. All PCs must reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with two central routers connected to each other. Each central router connects to two edge routers. Each edge router serves one LAN with three PCs. The two central routers do not serve any LAN directly. Use IPv4. Edge routers must use a default route pointing to their central router. The central routers must have explicit routes to all four edge LANs and to each other. All PCs must reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 05 — Dual-Stack Ring with Central Server

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, ring topology, central server, five routers, static routing

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with five routers in a ring. One of the routers also connects to a dedicated LAN with a central server. Each of the other four routers connects to one LAN with two clients. Use both IPv4 and IPv6 on every device. Write all routes manually for both address families. The central server must be reachable from every client using both IPv4 and IPv6. No dynamic routing is allowed.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with five routers in a ring. One of the routers also connects to a dedicated LAN with a central server. Each of the other four routers connects to one LAN with two clients. Use both IPv4 and IPv6 on every device. Write all routes manually for both address families. The central server must be reachable from every client using both IPv4 and IPv6. No dynamic routing is allowed.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 06 — IPv4 Tree with Three Levels, DNS Chain, Web Server

**Difficulty:** Advanced

**Main concepts:** IPv4, tree topology, three levels, root DNS, TLD DNS, authoritative DNS, local DNS, web server

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with seven routers arranged in a three-level tree. The root router connects to two second-level routers. Each second-level router connects to two third-level routers. The root router connects to a LAN with a root DNS server. One second-level router connects to a LAN with a DNS server for the net top-level domain. One third-level router connects to a LAN with an authoritative DNS server for campus.net and a web server for campus.net. Another third-level router connects to a LAN with a client and a local DNS server. Use IPv4 only. All routes must be static. The client must resolve campus.net through the full DNS chain and access the web server by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with seven routers arranged in a three-level tree. The root router connects to two second-level routers. Each second-level router connects to two third-level routers. The root router connects to a LAN with a root DNS server. One second-level router connects to a LAN with a DNS server for the net top-level domain. One third-level router connects to a LAN with an authoritative DNS server for campus.net and a web server for campus.net. Another third-level router connects to a LAN with a client and a local DNS server. Use IPv4 only. All routes must be static. The client must resolve campus.net through the full DNS chain and access the web server by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 07 — IPv4 Partial Mesh, Six Routers, Max Degree 3, No Default Routes

**Difficulty:** Advanced

**Main concepts:** IPv4, partial mesh, six routers, max degree 3, explicit routes, no default routes

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with six routers arranged in a partial mesh. No router may have more than three connections to other routers. Each router serves one LAN with two PCs. Use IPv4 only. Every router must have a complete routing table with explicit routes to every other network. Default routes are not allowed on any router. All twelve PCs must be able to reach every other PC.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with six routers arranged in a partial mesh. No router may have more than three connections to other routers. Each router serves one LAN with two PCs. Use IPv4 only. Every router must have a complete routing table with explicit routes to every other network. Default routes are not allowed on any router. All twelve PCs must be able to reach every other PC.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 08 — IPv6 Star with Switches and Many Clients

**Difficulty:** Medium

**Main concepts:** IPv6, star topology, switches, one central router, three LANs, multiple clients

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with one central router connected to three LANs. Each LAN has an Ethernet switch connecting five PCs. Use IPv6 only. Assign all IPv6 addresses statically. Write routes on the central router for all three LANs. Each PC must use a default route pointing to the central router. All fifteen PCs must be able to reach each other through the router and switches.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with one central router connected to three LANs. Each LAN has an Ethernet switch connecting five PCs. Use IPv6 only. Assign all IPv6 addresses statically. Write routes on the central router for all three LANs. Each PC must use a default route pointing to the central router. All fifteen PCs must be able to reach each other through the router and switches.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 09 — Dual-Stack Four-Router Line with Two Web Servers

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, linear topology, four routers, two web servers, static routing

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with four routers arranged in a line. The first router connects to a LAN with a web server for company.test. The last router connects to a LAN with a web server for research.org. The second and third routers each connect to one LAN with two clients. Use both IPv4 and IPv6. Write all routes manually for both address families. All clients must be able to reach both web servers by IP address using both IPv4 and IPv6.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with four routers arranged in a line. The first router connects to a LAN with a web server for company.test. The last router connects to a LAN with a web server for research.org. The second and third routers each connect to one LAN with two clients. Use both IPv4 and IPv6. Write all routes manually for both address families. All clients must be able to reach both web servers by IP address using both IPv4 and IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 10 — IPv4 Ring with Local DNS and Two Web Servers

**Difficulty:** Advanced

**Main concepts:** IPv4, ring topology, five routers, local DNS server, two web servers, two domains, static routing

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with five routers arranged in a ring. One router connects to a LAN with a client and a local DNS server. Two different routers each connect to a LAN with a web server. One web server hosts example.net and the other hosts university.edu. The remaining two routers each connect to a LAN with additional clients. Use IPv4 only. Write all routes by hand. The local DNS server must know the addresses of both web servers. Every client must be able to reach both web servers by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with five routers arranged in a ring. One router connects to a LAN with a client and a local DNS server. Two different routers each connect to a LAN with a web server. One web server hosts example.net and the other hosts university.edu. The remaining two routers each connect to a LAN with additional clients. Use IPv4 only. Write all routes by hand. The local DNS server must know the addresses of both web servers. Every client must be able to reach both web servers by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 11 — IPv4 Backbone with Two Branches

**Difficulty:** Medium

**Main concepts:** IPv4, backbone routers, branch topology, six routers, static routing, default routes

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with two backbone routers connected to each other. Each backbone router connects to two branch routers. Each branch router serves one LAN with two PCs. The backbone routers do not serve any LAN. Use IPv4. Branch routers must use a default route pointing to their backbone router. Backbone routers must have explicit routes to all branch LANs. All PCs must reach all other PCs across the backbone.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with two backbone routers connected to each other. Each backbone router connects to two branch routers. Each branch router serves one LAN with two PCs. The backbone routers do not serve any LAN. Use IPv4. Branch routers must use a default route pointing to their backbone router. Backbone routers must have explicit routes to all branch LANs. All PCs must reach all other PCs across the backbone.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 12 — IPv6 Diamond with Central Server and Explicit Routes

**Difficulty:** Medium

**Main concepts:** IPv6, diamond topology, four routers, central server, explicit routes, no default routes

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab using IPv6 only with four routers in a diamond shape. The top router connects to two middle routers, and both middle routers connect to the bottom router. The top router connects to a LAN with a central server. Each middle router connects to a LAN with two clients. The bottom router connects to a LAN with two additional clients. Write all IPv6 routes explicitly on every router. No default routes are allowed. Every client must reach the central server.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab using IPv6 only with four routers in a diamond shape. The top router connects to two middle routers, and both middle routers connect to the bottom router. The top router connects to a LAN with a central server. Each middle router connects to a LAN with two clients. The bottom router connects to a LAN with two additional clients. Write all IPv6 routes explicitly on every router. No default routes are allowed. Every client must reach the central server.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 13 — Dual-Stack Partial Mesh with DNS Full Chain

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, partial mesh, five routers, root DNS, TLD DNS, local DNS, web server

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with five routers connected in a partial mesh. No router may connect to more than three other routers. One router connects to a LAN with a root DNS server. Another router connects to a LAN with a DNS server for the org top-level domain. A third router connects to a LAN with an authoritative DNS server for kathara.org and a web server for kathara.org. A fourth router connects to a LAN with a client and a local DNS server. The fifth router is a transit router without a LAN. Use both IPv4 and IPv6. Write all routes manually for both address families. The client must resolve kathara.org through the DNS chain and access the web server by name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with five routers connected in a partial mesh. No router may connect to more than three other routers. One router connects to a LAN with a root DNS server. Another router connects to a LAN with a DNS server for the org top-level domain. A third router connects to a LAN with an authoritative DNS server for kathara.org and a web server for kathara.org. A fourth router connects to a LAN with a client and a local DNS server. The fifth router is a transit router without a LAN. Use both IPv4 and IPv6. Write all routes manually for both address families. The client must resolve kathara.org through the DNS chain and access the web server by name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 14 — IPv4 Three-Router Triangle with Switches and Many PCs

**Difficulty:** Medium

**Main concepts:** IPv4, triangle topology, three routers, switches, nine PCs, static routing

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with three routers connected in a triangle. Each router connects to every other router. Each router also connects to one LAN with an Ethernet switch and three PCs behind the switch. Use IPv4. Write all routes manually. No default routes are allowed. All nine PCs must be able to reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with three routers connected in a triangle. Each router connects to every other router. Each router also connects to one LAN with an Ethernet switch and three PCs behind the switch. Use IPv4. Write all routes manually. No default routes are allowed. All nine PCs must be able to reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 15 — IPv6 Tree with Edge Default Routes and Central Web Server

**Difficulty:** Medium

**Main concepts:** IPv6, tree topology, four routers, web server, default routes on edges, static routing

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab using IPv6 only. One root router connects to three leaf routers in a tree shape. The root router connects to a LAN with a web server. Each leaf router connects to one LAN with three clients. Use IPv6. The leaf routers must use a default route pointing to the root router. The root router must have explicit routes to all three leaf LANs. All clients must reach the web server.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab using IPv6 only. One root router connects to three leaf routers in a tree shape. The root router connects to a LAN with a web server. Each leaf router connects to one LAN with three clients. Use IPv6. The leaf routers must use a default route pointing to the root router. The root router must have explicit routes to all three leaf LANs. All clients must reach the web server.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 16 — IPv4 Six-Router Line with DNS and Web at Opposite Ends

**Difficulty:** Advanced

**Main concepts:** IPv4, linear topology, six routers, DNS, web server, long path, static routing

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with six routers arranged in a line. The first router connects to a LAN with a client, a local DNS server and a root DNS server. The sixth router connects to a LAN with a web server for training.lab and an authoritative DNS server for training.lab. Routers two through five are transit routers without LANs. Use IPv4. Write all routes by hand on every router. The client must resolve training.lab through DNS and reach the web server by domain name. No default routes are allowed on interior routers.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with six routers arranged in a line. The first router connects to a LAN with a client, a local DNS server and a root DNS server. The sixth router connects to a LAN with a web server for training.lab and an authoritative DNS server for training.lab. Routers two through five are transit routers without LANs. Use IPv4. Write all routes by hand on every router. The client must resolve training.lab through DNS and reach the web server by domain name. No default routes are allowed on interior routers.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 17 — Dual-Stack Diamond with Two Switches per LAN

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, diamond topology, switches, four routers, static routing

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with four routers in a diamond shape. Each router connects to one LAN. Each LAN has an Ethernet switch with four PCs behind it. Use both IPv4 and IPv6 on all devices. Write all routes manually for both address families. Every PC must be able to reach every other PC on both IPv4 and IPv6.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with four routers in a diamond shape. Each router connects to one LAN. Each LAN has an Ethernet switch with four PCs behind it. Use both IPv4 and IPv6 on all devices. Write all routes manually for both address families. Every PC must be able to reach every other PC on both IPv4 and IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 18 — IPv4 Star with Main Server and DNS Resolution

**Difficulty:** Medium

**Main concepts:** IPv4, star topology, one central router, main server, local DNS server, domain name

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with one central router and four edge routers. The central router connects to a LAN with a main server and a local DNS server. Each edge router connects to one LAN with two clients. Use IPv4. Edge routers use a default route pointing to the central router. The central router has explicit routes to all edge LANs. The DNS server must know the address of the main server for the domain service.local. All clients must reach the main server by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with one central router and four edge routers. The central router connects to a LAN with a main server and a local DNS server. Each edge router connects to one LAN with two clients. Use IPv4. Edge routers use a default route pointing to the central router. The central router has explicit routes to all edge LANs. The DNS server must know the address of the main server for the domain service.local. All clients must reach the main server by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 19 — IPv6 Partial Mesh, Four Routers, Two Central Servers

**Difficulty:** Advanced

**Main concepts:** IPv6, partial mesh, four routers, two central servers, static routing, explicit routes

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab using IPv6 only. Use four routers in a partial mesh where no router connects to more than two other routers. Two routers each connect to a LAN with a central server. The other two routers each connect to a LAN with three clients. Write all IPv6 routes explicitly. No default routes are allowed. Every client must be able to reach both central servers.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab using IPv6 only. Use four routers in a partial mesh where no router connects to more than two other routers. Two routers each connect to a LAN with a central server. The other two routers each connect to a LAN with three clients. Write all IPv6 routes explicitly. No default routes are allowed. Every client must be able to reach both central servers.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 20 — IPv4 Ring with Authoritative DNS for Three Domains

**Difficulty:** Advanced

**Main concepts:** IPv4, ring topology, six routers, root DNS, three authoritative DNS servers, three web servers, local DNS

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with six routers in a ring. One router connects to a LAN with a root DNS server. Three other routers each connect to a LAN with an authoritative DNS server and a web server: one for kathara.org, one for university.edu and one for company.test. Another router connects to a LAN with a client and a local DNS server. The sixth router has a LAN with two additional clients. Use IPv4 only. Write all routes manually. The client must be able to resolve all three domain names through the DNS chain and reach each web server by name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with six routers in a ring. One router connects to a LAN with a root DNS server. Three other routers each connect to a LAN with an authoritative DNS server and a web server: one for kathara.org, one for university.edu and one for company.test. Another router connects to a LAN with a client and a local DNS server. The sixth router has a LAN with two additional clients. Use IPv4 only. Write all routes manually. The client must be able to resolve all three domain names through the DNS chain and reach each web server by name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 21 — Dual-Stack Tree with Local DNS and Two Web Servers

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, tree topology, five routers, local DNS, two web servers, two domains

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with five routers in a tree. The root router connects to two second-level routers. Each second-level router connects to one third-level router. The root router connects to a LAN with a local DNS server. One third-level router connects to a LAN with a web server for library.test. The other third-level router connects to a LAN with a web server for research.org. Each second-level router connects to a LAN with two clients. Use both IPv4 and IPv6 on all devices. Write all routes manually for both address families. The DNS server must know both web server addresses. All clients must reach both web servers by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with five routers in a tree. The root router connects to two second-level routers. Each second-level router connects to one third-level router. The root router connects to a LAN with a local DNS server. One third-level router connects to a LAN with a web server for library.test. The other third-level router connects to a LAN with a web server for research.org. Each second-level router connects to a LAN with two clients. Use both IPv4 and IPv6 on all devices. Write all routes manually for both address families. The DNS server must know both web server addresses. All clients must reach both web servers by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 22 — IPv4 Partial Mesh with Transit Routers and Selective Connectivity

**Difficulty:** Advanced

**Main concepts:** IPv4, partial mesh, five routers, transit routers, selective connectivity, static routing

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with five routers. Three routers are transit routers without LANs. The other two routers each connect to one LAN. One LAN has a web server and two clients. The other LAN has three clients. The five routers are connected in a partial mesh where no router connects to more than three other routers. Use IPv4 only. Write all routes manually. The three clients in the second LAN must be able to reach the web server, but the two clients in the first LAN only need to reach each other and the web server in their own LAN. All routes must be explicitly defined.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with five routers. Three routers are transit routers without LANs. The other two routers each connect to one LAN. One LAN has a web server and two clients. The other LAN has three clients. The five routers are connected in a partial mesh where no router connects to more than three other routers. Use IPv4 only. Write all routes manually. The three clients in the second LAN must be able to reach the web server, but the two clients in the first LAN only need to reach each other and the web server in their own LAN. All routes must be explicitly defined.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 23 — IPv6 Ring with Central Server and Local DNS

**Difficulty:** Medium

**Main concepts:** IPv6, ring topology, four routers, central server, local DNS, domain name, static routing

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab using IPv6 only with four routers in a ring. One router connects to a LAN with a central server for the domain service.local. Another router connects to a LAN with a local DNS server and two clients. The other two routers each connect to one LAN with two additional clients. The DNS server must know the address of the central server. Write all IPv6 routes manually. All clients must reach the central server by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab using IPv6 only with four routers in a ring. One router connects to a LAN with a central server for the domain service.local. Another router connects to a LAN with a local DNS server and two clients. The other two routers each connect to one LAN with two additional clients. The DNS server must know the address of the central server. Write all IPv6 routes manually. All clients must reach the central server by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 24 — IPv4 Two-Tier Tree with Switches, Web Server and DNS

**Difficulty:** Medium

**Main concepts:** IPv4, tree topology, three routers, switches, web server, local DNS, static routing

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with one root router connected to two leaf routers. The root router connects to a LAN with a web server for campus.net. Each leaf router connects to a LAN with an Ethernet switch and four PCs behind the switch. One leaf LAN also includes a local DNS server. Use IPv4. The leaf routers must use a default route to the root router. The root router must have explicit routes. The local DNS server must know the address of the web server. All PCs must access campus.net by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with one root router connected to two leaf routers. The root router connects to a LAN with a web server for campus.net. Each leaf router connects to a LAN with an Ethernet switch and four PCs behind the switch. One leaf LAN also includes a local DNS server. Use IPv4. The leaf routers must use a default route to the root router. The root router must have explicit routes. The local DNS server must know the address of the web server. All PCs must access campus.net by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 25 — Dual-Stack Six-Router Partial Mesh with Central Server

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, partial mesh, six routers, central server, max degree 3, static routing

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with six routers in a partial mesh. No router may connect to more than three other routers. One router connects to a LAN with a central server. Each of the other five routers connects to one LAN with two clients. Use both IPv4 and IPv6 on all devices. Write all routes manually for both address families. Every client must be able to reach the central server on both IPv4 and IPv6. No default routes are allowed.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with six routers in a partial mesh. No router may connect to more than three other routers. One router connects to a LAN with a central server. Each of the other five routers connects to one LAN with two clients. Use both IPv4 and IPv6 on all devices. Write all routes manually for both address families. Every client must be able to reach the central server on both IPv4 and IPv6. No default routes are allowed.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 26 — IPv4 Five-Router Ring, Two Web Servers, Authoritative DNS for Each

**Difficulty:** Advanced

**Main concepts:** IPv4, ring topology, five routers, two web servers, two authoritative DNS servers, root DNS, local DNS

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with five routers in a ring. One router connects to a LAN with a root DNS server. Two other routers each connect to a LAN containing both a web server and its authoritative DNS server: one for research.org and one for example.net. A fourth router connects to a LAN with a local DNS server and two clients. The fifth router connects to a LAN with two additional clients. Use IPv4 only. Write all routes manually. The clients must resolve both domains through the full DNS chain and reach each web server by name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with five routers in a ring. One router connects to a LAN with a root DNS server. Two other routers each connect to a LAN containing both a web server and its authoritative DNS server: one for research.org and one for example.net. A fourth router connects to a LAN with a local DNS server and two clients. The fifth router connects to a LAN with two additional clients. Use IPv4 only. Write all routes manually. The clients must resolve both domains through the full DNS chain and reach each web server by name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 27 — IPv6 Line with Switches, Explicit Routes, No Default Routes

**Difficulty:** Medium

**Main concepts:** IPv6, linear topology, three routers, switches, explicit routes, no default routes

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab using IPv6 only. Arrange three routers in a line. Each router connects to one LAN with an Ethernet switch and four PCs behind the switch. Write all IPv6 routes explicitly on every router. No default routes are allowed. All twelve PCs must reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab using IPv6 only. Arrange three routers in a line. Each router connects to one LAN with an Ethernet switch and four PCs behind the switch. Write all IPv6 routes explicitly on every router. No default routes are allowed. All twelve PCs must reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 28 — IPv4 Five-Router Tree, Main Server, DNS, and Web Server Combined

**Difficulty:** Advanced

**Main concepts:** IPv4, tree topology, five routers, main server, DNS, web server, combined services

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with five routers in a tree. One root router connects to two second-level routers. Each second-level router connects to one third-level router. The root router connects to a LAN with a main server. One third-level router connects to a LAN with a web server for company.test, its authoritative DNS server and a root DNS server. The other third-level router connects to a LAN with a client and a local DNS server. Each second-level router connects to a LAN with two additional clients. Use IPv4. Write all routes manually. Every client must reach the main server by IP. The client with the local DNS server must also access company.test by domain name through the DNS chain.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with five routers in a tree. One root router connects to two second-level routers. Each second-level router connects to one third-level router. The root router connects to a LAN with a main server. One third-level router connects to a LAN with a web server for company.test, its authoritative DNS server and a root DNS server. The other third-level router connects to a LAN with a client and a local DNS server. Each second-level router connects to a LAN with two additional clients. Use IPv4. Write all routes manually. Every client must reach the main server by IP. The client with the local DNS server must also access company.test by domain name through the DNS chain.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 29 — Dual-Stack Ring, Five Routers, Mixed Default and Explicit Routes

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, ring topology, five routers, mixed default and explicit routes

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with five routers in a ring. Each router connects to one LAN with two PCs. Use both IPv4 and IPv6 on all devices. Two routers must be designated as core routers with complete explicit routes to all networks. The other three routers must use a default route pointing toward the nearest core router. Write all routes manually for both address families. All PCs must reach all other PCs on both IPv4 and IPv6.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with five routers in a ring. Each router connects to one LAN with two PCs. Use both IPv4 and IPv6 on all devices. Two routers must be designated as core routers with complete explicit routes to all networks. The other three routers must use a default route pointing toward the nearest core router. Write all routes manually for both address families. All PCs must reach all other PCs on both IPv4 and IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 30 — IPv4 Asymmetric Tree with Uneven Branches

**Difficulty:** Medium

**Main concepts:** IPv4, asymmetric tree, five routers, uneven branches, static routing

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with five routers in an asymmetric tree. The root router connects to two child routers. The first child router connects to two additional routers in a second level. The second child router has no further children. The root router has one LAN with one PC. The first child router has one LAN with two PCs. The two second-level routers each have one LAN with three PCs. The second child router has one LAN with two PCs. Use IPv4. Write all routes explicitly. No default routes. All PCs must reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with five routers in an asymmetric tree. The root router connects to two child routers. The first child router connects to two additional routers in a second level. The second child router has no further children. The root router has one LAN with one PC. The first child router has one LAN with two PCs. The two second-level routers each have one LAN with three PCs. The second child router has one LAN with two PCs. Use IPv4. Write all routes explicitly. No default routes. All PCs must reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 31 — IPv6 Five-Router Partial Mesh with Web Server and Switches

**Difficulty:** Advanced

**Main concepts:** IPv6, partial mesh, five routers, web server, switches, max degree 3, static routing

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab using IPv6 only with five routers in a partial mesh. No router may connect to more than three other routers. One router connects to a LAN with a web server. Three routers each connect to one LAN with an Ethernet switch and three clients behind the switch. One router is a transit router without a LAN. Write all IPv6 routes manually. All clients must reach the web server by its IP address. No default routes are allowed.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab using IPv6 only with five routers in a partial mesh. No router may connect to more than three other routers. One router connects to a LAN with a web server. Three routers each connect to one LAN with an Ethernet switch and three clients behind the switch. One router is a transit router without a LAN. Write all IPv6 routes manually. All clients must reach the web server by its IP address. No default routes are allowed.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 32 — IPv4 Star-of-Stars, Two Levels of Routing

**Difficulty:** Advanced

**Main concepts:** IPv4, star topology, two levels, seven routers, default routes, static routing

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with one core router, two distribution routers and four access routers. The core router connects to both distribution routers. Each distribution router connects to two access routers. Each access router serves one LAN with three PCs. The core and distribution routers do not serve any LAN. Use IPv4. Access routers must use a default route toward their distribution router. Distribution routers must use a default route toward the core router and explicit routes toward their access LANs. The core router must have explicit routes to all access LANs. All PCs must reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with one core router, two distribution routers and four access routers. The core router connects to both distribution routers. Each distribution router connects to two access routers. Each access router serves one LAN with three PCs. The core and distribution routers do not serve any LAN. Use IPv4. Access routers must use a default route toward their distribution router. Distribution routers must use a default route toward the core router and explicit routes toward their access LANs. The core router must have explicit routes to all access LANs. All PCs must reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 33 — Dual-Stack Line, Five Routers, Central Server and Web Server

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, linear topology, five routers, central server, web server, static routing

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with five routers in a line. The first router connects to a LAN with a central server. The fifth router connects to a LAN with a web server. The middle three routers each connect to one LAN with two clients. Use both IPv4 and IPv6 on all devices. Write all routes manually for both address families. Every client must reach both the central server and the web server using both IPv4 and IPv6. No default routes are allowed.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with five routers in a line. The first router connects to a LAN with a central server. The fifth router connects to a LAN with a web server. The middle three routers each connect to one LAN with two clients. Use both IPv4 and IPv6 on all devices. Write all routes manually for both address families. Every client must reach both the central server and the web server using both IPv4 and IPv6. No default routes are allowed.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 34 — IPv4 Ring with Two Local DNS Servers in Different LANs

**Difficulty:** Medium

**Main concepts:** IPv4, ring topology, four routers, two local DNS servers, web server, static routing

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with four routers in a ring. One router connects to a LAN with a web server for network.lab. Two other routers each connect to a LAN with clients and a local DNS server. The fourth router connects to a LAN with two additional clients that use one of the existing local DNS servers. Both local DNS servers must know the address of the web server. Use IPv4. Write all routes manually. All clients must access network.lab by domain name, each using its own local DNS server.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with four routers in a ring. One router connects to a LAN with a web server for network.lab. Two other routers each connect to a LAN with clients and a local DNS server. The fourth router connects to a LAN with two additional clients that use one of the existing local DNS servers. Both local DNS servers must know the address of the web server. Use IPv4. Write all routes manually. All clients must access network.lab by domain name, each using its own local DNS server.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 35 — IPv6 Tree, Four Routers, Central Server Plus DNS

**Difficulty:** Medium

**Main concepts:** IPv6, tree topology, four routers, central server, local DNS server, domain name

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab using IPv6 only with four routers in a tree. The root router connects to three child routers. The root router connects to a LAN with a central server for the domain service.local and a local DNS server. Each child router connects to one LAN with three clients. Write all IPv6 routes manually. The DNS server must know the address of the central server. All clients must reach the central server by domain name. Edge routers may use a default route.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab using IPv6 only with four routers in a tree. The root router connects to three child routers. The root router connects to a LAN with a central server for the domain service.local and a local DNS server. Each child router connects to one LAN with three clients. Write all IPv6 routes manually. The DNS server must know the address of the central server. All clients must reach the central server by domain name. Edge routers may use a default route.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 36 — IPv4 Partial Mesh, Five Routers, Two Web Servers, Selective Client Access

**Difficulty:** Advanced

**Main concepts:** IPv4, partial mesh, five routers, two web servers, selective access, static routing

**Version A**

```text
Generate a detailed prompt file for this request: design a Kathara lab with five routers in a partial mesh. No router connects to more than three other routers. One router connects to a LAN with a web server for kathara.org. Another router connects to a LAN with a web server for example.net. Two other routers each connect to a LAN with three clients. The fifth router is a transit router. Use IPv4. Write all routes manually. The clients in the first LAN must reach only kathara.org. The clients in the second LAN must reach only example.net. No client needs access to the other web server.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a Kathara lab with five routers in a partial mesh. No router connects to more than three other routers. One router connects to a LAN with a web server for kathara.org. Another router connects to a LAN with a web server for example.net. Two other routers each connect to a LAN with three clients. The fifth router is a transit router. Use IPv4. Write all routes manually. The clients in the first LAN must reach only kathara.org. The clients in the second LAN must reach only example.net. No client needs access to the other web server.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 37 — Dual-Stack Ring, Six Routers, Full DNS Chain, Web Server

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, ring topology, six routers, root DNS, TLD DNS, authoritative DNS, local DNS, web server

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab with six routers in a ring. Use both IPv4 and IPv6 on all devices. One router connects to a LAN with a root DNS server. Another connects to a LAN with a DNS server for the edu top-level domain. A third connects to a LAN with an authoritative DNS server for university.edu and a web server for university.edu. A fourth connects to a LAN with a local DNS server and two clients. The remaining two routers each connect to a LAN with two additional clients. Write all routes manually for both address families. All clients must resolve university.edu through the full DNS chain and access the web server by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab with six routers in a ring. Use both IPv4 and IPv6 on all devices. One router connects to a LAN with a root DNS server. Another connects to a LAN with a DNS server for the edu top-level domain. A third connects to a LAN with an authoritative DNS server for university.edu and a web server for university.edu. A fourth connects to a LAN with a local DNS server and two clients. The remaining two routers each connect to a LAN with two additional clients. Write all routes manually for both address families. All clients must resolve university.edu through the full DNS chain and access the web server by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 38 — IPv4 Three-Router Line with Two Switches and Eight PCs

**Difficulty:** Medium

**Main concepts:** IPv4, linear topology, three routers, two switches, eight PCs, static routing

**Version A**

```text
Generate a detailed prompt file for this request: create a Kathara lab with three routers in a line. The first router connects to a LAN with an Ethernet switch and four PCs behind the switch. The third router connects to a LAN with another Ethernet switch and four PCs behind it. The middle router connects to both the first and third routers and has no LAN. Use IPv4. Write all routes manually. No default routes on the middle router. Edge routers may use a default route. All eight PCs must reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: create a Kathara lab with three routers in a line. The first router connects to a LAN with an Ethernet switch and four PCs behind the switch. The third router connects to a LAN with another Ethernet switch and four PCs behind it. The middle router connects to both the first and third routers and has no LAN. Use IPv4. Write all routes manually. No default routes on the middle router. Edge routers may use a default route. All eight PCs must reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 39 — IPv6 Partial Mesh, Five Routers, DNS and Central Server

**Difficulty:** Advanced

**Main concepts:** IPv6, partial mesh, five routers, root DNS, authoritative DNS, local DNS, central server, domain name

**Version A**

```text
Generate a detailed prompt file for this request: build a Kathara lab using IPv6 only with five routers in a partial mesh. No router may connect to more than three other routers. One router connects to a LAN with a root DNS server and an authoritative DNS server for research.org. Another router connects to a LAN with a central server hosting research.org. A third router connects to a LAN with a local DNS server and two clients. The remaining two routers each connect to a LAN with two additional clients. Write all IPv6 routes manually. The clients with the local DNS server must resolve research.org through DNS and access the central server by domain name. All other clients must reach the central server by IP address.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: build a Kathara lab using IPv6 only with five routers in a partial mesh. No router may connect to more than three other routers. One router connects to a LAN with a root DNS server and an authoritative DNS server for research.org. Another router connects to a LAN with a central server hosting research.org. A third router connects to a LAN with a local DNS server and two clients. The remaining two routers each connect to a LAN with two additional clients. Write all IPv6 routes manually. The clients with the local DNS server must resolve research.org through DNS and access the central server by domain name. All other clients must reach the central server by IP address.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 40 — Large Dual-Stack Lab: Seven Routers, DNS, Two Web Servers, Central Server

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, seven routers, partial mesh, root DNS, TLD DNS, two authoritative DNS, two web servers, central server, local DNS

**Version A**

```text
Generate a detailed prompt file for this request: design a large Kathara lab with seven routers in a partial mesh. No router may connect to more than three other routers. Use both IPv4 and IPv6 on all devices. One router connects to a LAN with a root DNS server. Another connects to a LAN with a DNS server for the test top-level domain. Two routers each connect to a LAN with a web server and its authoritative DNS server: one for company.test and one for library.test. One router connects to a LAN with a central server. One router connects to a LAN with a local DNS server and three clients. The last router connects to a LAN with two additional clients. Write all routes manually for both address families. The clients with the local DNS server must resolve both company.test and library.test through the full DNS chain and access both web servers by domain name. All clients must also reach the central server by IP. No default routes are allowed.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: design a large Kathara lab with seven routers in a partial mesh. No router may connect to more than three other routers. Use both IPv4 and IPv6 on all devices. One router connects to a LAN with a root DNS server. Another connects to a LAN with a DNS server for the test top-level domain. Two routers each connect to a LAN with a web server and its authoritative DNS server: one for company.test and one for library.test. One router connects to a LAN with a central server. One router connects to a LAN with a local DNS server and three clients. The last router connects to a LAN with two additional clients. Write all routes manually for both address families. The clients with the local DNS server must resolve both company.test and library.test through the full DNS chain and access both web servers by domain name. All clients must also reach the central server by IP. No default routes are allowed.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---
