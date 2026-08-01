# Kathara Lab Mini-Prompt Collection — Simple Natural Language, Set 2

> **40 distinct scenarios** — Medium and Advanced only.
> Each with Version A and Version B.
> All scenarios use static routing only. No dynamic protocols.
> All scenarios are different from those in small_prompts_simple_natural_language1.md.
> All prompts use simple, everyday English.

---

### Scenario 01 — Diamond Topology, Dual-Stack, Four Routers

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, diamond topology, four routers, static routing

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with four routers in a diamond shape. One router at the top connects to two routers in the middle. Both middle routers connect to one router at the bottom. Each router has one LAN with two PCs. Use both IPv4 and IPv6 on everything. Write all routes by hand for both protocols. Do not use default routes. Every PC must reach every other PC on both IPv4 and IPv6.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with four routers in a diamond shape. One router at the top connects to two routers in the middle. Both middle routers connect to one router at the bottom. Each router has one LAN with two PCs. Use both IPv4 and IPv6 on everything. Write all routes by hand for both protocols. Do not use default routes. Every PC must reach every other PC on both IPv4 and IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 02 — Four Routers, Partial Mesh, Redundant Paths, Web Server, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, partial mesh, redundant paths, web server, four routers, static routing

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with four routers connected so that there are at least two different paths between any two routers. No router should connect to more than three others. One router has a LAN with a web server. Two routers each have a LAN with two clients. The last router has no LAN and only passes traffic. Use IPv4. Write all routes by hand. Every client must reach the web server.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with four routers connected so that there are at least two different paths between any two routers. No router should connect to more than three others. One router has a LAN with a web server. Two routers each have a LAN with two clients. The last router has no LAN and only passes traffic. Use IPv4. Write all routes by hand. Every client must reach the web server.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 03 — Five Routers in a Line, IPv6, DNS and Web Server at Opposite Ends

**Difficulty:** Advanced

**Main concepts:** IPv6, linear topology, five routers, DNS, web server, long path

**Version A**

```text
Generate a detailed prompt file for this request: Make a lab with five routers in a line using IPv6 only. The first router has a LAN with a client and a local DNS server. The last router has a LAN with a web server for network.lab. The three routers in the middle just pass traffic and have no LANs. Write all IPv6 routes by hand. The client must find network.lab through DNS and open the web page. Edge routers can use a default route but middle routers cannot.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Make a lab with five routers in a line using IPv6 only. The first router has a LAN with a client and a local DNS server. The last router has a LAN with a web server for network.lab. The three routers in the middle just pass traffic and have no LANs. Write all IPv6 routes by hand. The client must find network.lab through DNS and open the web page. Edge routers can use a default route but middle routers cannot.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 04 — Two Backbone Routers, Four Branch Routers, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, backbone routers, branch topology, six routers, default routes

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with two backbone routers connected to each other. Each backbone router connects to two branch routers. Each branch router has one LAN with three PCs. The backbone routers have no LANs of their own. Use IPv4. Branch routers should use a default route to their backbone router. Backbone routers need explicit routes to reach every branch LAN. All PCs must be able to reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with two backbone routers connected to each other. Each backbone router connects to two branch routers. Each branch router has one LAN with three PCs. The backbone routers have no LANs of their own. Use IPv4. Branch routers should use a default route to their backbone router. Backbone routers need explicit routes to reach every branch LAN. All PCs must be able to reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 05 — Five Routers in a Ring, Central Server, Dual-Stack

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, ring topology, five routers, central server

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with five routers in a ring. One router also connects to a LAN with a central server. The other four routers each connect to one LAN with two clients. Use both IPv4 and IPv6 on every device. Write all routes by hand for both protocols. The central server must be reachable from every client using both IPv4 and IPv6.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with five routers in a ring. One router also connects to a LAN with a central server. The other four routers each connect to one LAN with two clients. Use both IPv4 and IPv6 on every device. Write all routes by hand for both protocols. The central server must be reachable from every client using both IPv4 and IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 06 — Seven-Router Tree, Three-Level DNS Chain, Web Server, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, tree topology, seven routers, root DNS, TLD DNS, authoritative DNS, local DNS, web server

**Version A**

```text
Generate a detailed prompt file for this request: Make a lab with seven routers in a tree with three levels. The root router connects to two second-level routers. Each second-level router connects to two third-level routers. The root router has a LAN with a root DNS server. One second-level router has a LAN with a DNS server for the net domain. One third-level router has a LAN with an authoritative DNS server for campus.net and a web server for campus.net. Another third-level router has a LAN with a client and a local DNS server. Use IPv4. Write all routes by hand. The client must find campus.net through all three DNS levels and open the web page.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Make a lab with seven routers in a tree with three levels. The root router connects to two second-level routers. Each second-level router connects to two third-level routers. The root router has a LAN with a root DNS server. One second-level router has a LAN with a DNS server for the net domain. One third-level router has a LAN with an authoritative DNS server for campus.net and a web server for campus.net. Another third-level router has a LAN with a client and a local DNS server. Use IPv4. Write all routes by hand. The client must find campus.net through all three DNS levels and open the web page.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 07 — Six Routers, Partial Mesh, Max Degree 3, No Default Routes, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, partial mesh, six routers, connection limit, explicit routes, no default routes

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with six routers connected in a partial mesh. No router should connect to more than three other routers. Each router has one LAN with two PCs. Use IPv4. Write a complete routing table on every router with a route for every network. Do not use default routes on any router. All PCs must reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with six routers connected in a partial mesh. No router should connect to more than three other routers. Each router has one LAN with two PCs. Use IPv4. Write a complete routing table on every router with a route for every network. Do not use default routes on any router. All PCs must reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 08 — One Central Router, Three LANs with Switches, IPv6, Many Clients

**Difficulty:** Medium

**Main concepts:** IPv6, star topology, switches, one router, three LANs, fifteen PCs

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with one central router connected to three LANs. Each LAN has a switch with five PCs behind it. Use IPv6 only. Give all addresses by hand. The router needs routes for all three LANs. Each PC should use a default route to the router. All fifteen PCs must reach each other through the switch and the router.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with one central router connected to three LANs. Each LAN has a switch with five PCs behind it. Use IPv6 only. Give all addresses by hand. The router needs routes for all three LANs. Each PC should use a default route to the router. All fifteen PCs must reach each other through the switch and the router.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 09 — Four Routers in a Line, Two Web Servers at Both Ends, Dual-Stack

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, linear topology, four routers, two web servers

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with four routers in a line. The first router has a LAN with a web server for company.test. The last router has a LAN with a web server for research.org. The two middle routers each have a LAN with two clients. Use both IPv4 and IPv6 on all devices. Write all routes by hand for both protocols. All clients must reach both web servers using both IPv4 and IPv6.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with four routers in a line. The first router has a LAN with a web server for company.test. The last router has a LAN with a web server for research.org. The two middle routers each have a LAN with two clients. Use both IPv4 and IPv6 on all devices. Write all routes by hand for both protocols. All clients must reach both web servers using both IPv4 and IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 10 — Five Routers in a Ring, Local DNS, Two Web Servers, Two Domains, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, ring topology, five routers, local DNS, two web servers, two domains

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with five routers in a ring. One router has a LAN with a client and a local DNS server. Two other routers each have a LAN with a web server — one for example.net and one for university.edu. The last two routers each have a LAN with extra clients. Use IPv4. Write all routes by hand. The local DNS server must know the addresses of both web servers. Every client must open both web servers by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with five routers in a ring. One router has a LAN with a client and a local DNS server. Two other routers each have a LAN with a web server — one for example.net and one for university.edu. The last two routers each have a LAN with extra clients. Use IPv4. Write all routes by hand. The local DNS server must know the addresses of both web servers. Every client must open both web servers by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 11 — IPv4 Diamond with Central Server, No Default Routes

**Difficulty:** Medium

**Main concepts:** IPv6, diamond topology, four routers, central server, explicit routes

**Version A**

```text
Generate a detailed prompt file for this request: Make a lab using IPv6 only with four routers in a diamond shape. The top router has a LAN with a central server. Each middle router has a LAN with two clients. The bottom router has a LAN with two more clients. Write all IPv6 routes on every router. Do not use default routes. Every client must be able to reach the central server.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Make a lab using IPv6 only with four routers in a diamond shape. The top router has a LAN with a central server. Each middle router has a LAN with two clients. The bottom router has a LAN with two more clients. Write all IPv6 routes on every router. Do not use default routes. Every client must be able to reach the central server.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 12 — Dual-Stack Partial Mesh, Five Routers, Full DNS Chain

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, partial mesh, five routers, root DNS, TLD DNS, local DNS, web server

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with five routers in a partial mesh. No router connects to more than three others. One router has a LAN with a root DNS server. Another has a LAN with a DNS server for the org domain. A third has a LAN with an authoritative DNS server for kathara.org and a web server for kathara.org. A fourth has a LAN with a client and a local DNS server. The fifth router just passes traffic. Use both IPv4 and IPv6. Write all routes by hand for both protocols. The client must find kathara.org through DNS and open the web server by name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with five routers in a partial mesh. No router connects to more than three others. One router has a LAN with a root DNS server. Another has a LAN with a DNS server for the org domain. A third has a LAN with an authoritative DNS server for kathara.org and a web server for kathara.org. A fourth has a LAN with a client and a local DNS server. The fifth router just passes traffic. Use both IPv4 and IPv6. Write all routes by hand for both protocols. The client must find kathara.org through DNS and open the web server by name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 13 — Three Routers in a Triangle, Switches and Many PCs, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, triangle topology, three routers, switches, nine PCs, static routing

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with three routers connected in a triangle — each one connects to the other two. Each router also has a LAN with a switch and three PCs behind the switch. Use IPv4. Write all routes by hand. Do not use default routes. All nine PCs must reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with three routers connected in a triangle — each one connects to the other two. Each router also has a LAN with a switch and three PCs behind the switch. Use IPv4. Write all routes by hand. Do not use default routes. All nine PCs must reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 14 — IPv6 Tree, One Root, Three Leaves, Web Server, Default Routes

**Difficulty:** Medium

**Main concepts:** IPv6, tree topology, four routers, web server, default routes on leaves

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab using IPv6 only. One root router connects to three leaf routers. The root router has a LAN with a web server. Each leaf router has a LAN with three clients. Leaf routers should use a default route pointing to the root router. The root router must have explicit routes to all three leaf LANs. All clients must reach the web server.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab using IPv6 only. One root router connects to three leaf routers. The root router has a LAN with a web server. Each leaf router has a LAN with three clients. Leaf routers should use a default route pointing to the root router. The root router must have explicit routes to all three leaf LANs. All clients must reach the web server.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 15 — Six Routers in a Line, DNS and Web Server Far Apart, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, linear topology, six routers, DNS, web server, long path, transit routers

**Version A**

```text
Generate a detailed prompt file for this request: Make a lab with six routers in a line. The first router has a LAN with a client, a local DNS server and a root DNS server. The sixth router has a LAN with a web server for training.lab and its authoritative DNS server. The four routers in between just pass traffic. Use IPv4. Write all routes by hand. The client must find training.lab through DNS and open the web page. Do not use default routes on the middle routers.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Make a lab with six routers in a line. The first router has a LAN with a client, a local DNS server and a root DNS server. The sixth router has a LAN with a web server for training.lab and its authoritative DNS server. The four routers in between just pass traffic. Use IPv4. Write all routes by hand. The client must find training.lab through DNS and open the web page. Do not use default routes on the middle routers.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 16 — Dual-Stack Diamond, Switches in Every LAN

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, diamond topology, four routers, switches, many PCs

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with four routers in a diamond shape. Each router has one LAN with a switch and four PCs behind the switch. Use both IPv4 and IPv6 on everything. Write all routes by hand for both protocols. Every PC must reach every other PC on both IPv4 and IPv6.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with four routers in a diamond shape. Each router has one LAN with a switch and four PCs behind the switch. Use both IPv4 and IPv6 on everything. Write all routes by hand for both protocols. Every PC must reach every other PC on both IPv4 and IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 17 — Star Topology, Central Router, Main Server and DNS, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, star topology, central router, main server, local DNS, domain name, default routes

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with one central router and four edge routers. The central router has a LAN with a main server and a local DNS server. Each edge router has one LAN with two clients. Use IPv4. Edge routers should use a default route to the central router. The central router needs explicit routes to every edge LAN. The DNS server must know the address of the main server for the domain service.local. All clients must reach the main server by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with one central router and four edge routers. The central router has a LAN with a main server and a local DNS server. Each edge router has one LAN with two clients. Use IPv4. Edge routers should use a default route to the central router. The central router needs explicit routes to every edge LAN. The DNS server must know the address of the main server for the domain service.local. All clients must reach the main server by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 18 — IPv6 Partial Mesh, Four Routers, Two Central Servers

**Difficulty:** Advanced

**Main concepts:** IPv6, partial mesh, four routers, two central servers, explicit routes

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab using IPv6 only with four routers in a partial mesh. No router connects to more than two others. Two routers each have a LAN with a central server. The other two routers each have a LAN with three clients. Write all IPv6 routes on every router. Do not use default routes. Every client must reach both central servers.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab using IPv6 only with four routers in a partial mesh. No router connects to more than two others. Two routers each have a LAN with a central server. The other two routers each have a LAN with three clients. Write all IPv6 routes on every router. Do not use default routes. Every client must reach both central servers.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 19 — Six Routers in a Ring, Three Domains, Three Web Servers, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, ring topology, six routers, root DNS, three authoritative DNS, three web servers, local DNS

**Version A**

```text
Generate a detailed prompt file for this request: Make a lab with six routers in a ring. One router has a LAN with a root DNS server. Three other routers each have a LAN with an authoritative DNS server and a web server — one for kathara.org, one for university.edu and one for company.test. Another router has a LAN with a client and a local DNS server. The sixth router has a LAN with two extra clients. Use IPv4. Write all routes by hand. The client must find all three domain names through DNS and reach each web server by name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Make a lab with six routers in a ring. One router has a LAN with a root DNS server. Three other routers each have a LAN with an authoritative DNS server and a web server — one for kathara.org, one for university.edu and one for company.test. Another router has a LAN with a client and a local DNS server. The sixth router has a LAN with two extra clients. Use IPv4. Write all routes by hand. The client must find all three domain names through DNS and reach each web server by name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 20 — Dual-Stack Tree, Five Routers, Local DNS, Two Web Servers

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, tree topology, five routers, local DNS, two web servers, two domains

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with five routers in a tree. The root router connects to two second-level routers. Each second-level router connects to one leaf router. The root router has a LAN with a local DNS server. One leaf router has a LAN with a web server for library.test. The other leaf router has a LAN with a web server for research.org. Each second-level router has a LAN with two clients. Use both IPv4 and IPv6. Write all routes by hand for both protocols. The DNS server must know the addresses of both web servers. All clients must reach both web servers by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with five routers in a tree. The root router connects to two second-level routers. Each second-level router connects to one leaf router. The root router has a LAN with a local DNS server. One leaf router has a LAN with a web server for library.test. The other leaf router has a LAN with a web server for research.org. Each second-level router has a LAN with two clients. Use both IPv4 and IPv6. Write all routes by hand for both protocols. The DNS server must know the addresses of both web servers. All clients must reach both web servers by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 21 — Five Routers, Partial Mesh, Transit Routers, Selective Access, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, partial mesh, five routers, transit routers, selective connectivity

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with five routers. Three routers have no LANs and only pass traffic. One router has a LAN with a web server and two clients. Another router has a LAN with three clients. The routers are connected in a partial mesh where no router connects to more than three others. Use IPv4. Write all routes by hand. The three clients must reach the web server. The two clients in the web server LAN only need to reach the web server and each other. All routes must be written out — no default routes.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with five routers. Three routers have no LANs and only pass traffic. One router has a LAN with a web server and two clients. Another router has a LAN with three clients. The routers are connected in a partial mesh where no router connects to more than three others. Use IPv4. Write all routes by hand. The three clients must reach the web server. The two clients in the web server LAN only need to reach the web server and each other. All routes must be written out — no default routes.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 22 — IPv6 Ring, Four Routers, Central Server and Local DNS

**Difficulty:** Medium

**Main concepts:** IPv6, ring topology, four routers, central server, local DNS, domain name

**Version A**

```text
Generate a detailed prompt file for this request: Make a lab using IPv6 only with four routers in a ring. One router has a LAN with a central server for the domain service.local. Another router has a LAN with a local DNS server and two clients. The other two routers each have a LAN with two more clients. The DNS server must know the address of the central server. Write all IPv6 routes by hand. All clients must reach the central server by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Make a lab using IPv6 only with four routers in a ring. One router has a LAN with a central server for the domain service.local. Another router has a LAN with a local DNS server and two clients. The other two routers each have a LAN with two more clients. The DNS server must know the address of the central server. Write all IPv6 routes by hand. All clients must reach the central server by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 23 — Tree with Switches, Web Server, Local DNS, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, tree topology, three routers, switches, web server, local DNS, default routes

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with one root router connected to two leaf routers. The root router has a LAN with a web server for campus.net. Each leaf router has a LAN with a switch and four PCs behind the switch. One of the leaf LANs also has a local DNS server. Use IPv4. Leaf routers should use a default route to the root router. The root router needs explicit routes. The DNS server must know the web server address. All PCs must access campus.net by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with one root router connected to two leaf routers. The root router has a LAN with a web server for campus.net. Each leaf router has a LAN with a switch and four PCs behind the switch. One of the leaf LANs also has a local DNS server. Use IPv4. Leaf routers should use a default route to the root router. The root router needs explicit routes. The DNS server must know the web server address. All PCs must access campus.net by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 24 — Dual-Stack Partial Mesh, Six Routers, Central Server, Max Degree 3

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, partial mesh, six routers, central server, connection limit, no default routes

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with six routers in a partial mesh. No router connects to more than three others. One router has a LAN with a central server. Each of the other five routers has a LAN with two clients. Use both IPv4 and IPv6 on everything. Write all routes by hand for both protocols. Do not use default routes. Every client must reach the central server on both IPv4 and IPv6.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with six routers in a partial mesh. No router connects to more than three others. One router has a LAN with a central server. Each of the other five routers has a LAN with two clients. Use both IPv4 and IPv6 on everything. Write all routes by hand for both protocols. Do not use default routes. Every client must reach the central server on both IPv4 and IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 25 — Five Routers in a Ring, Two Authoritative DNS, Two Web Servers, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, ring topology, five routers, root DNS, two authoritative DNS, two web servers, local DNS

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with five routers in a ring. One router has a LAN with a root DNS server. Two other routers each have a LAN with a web server and its authoritative DNS server — one for research.org and one for example.net. A fourth router has a LAN with a local DNS server and two clients. The fifth router has a LAN with two more clients. Use IPv4. Write all routes by hand. The clients must find both domain names through the full DNS chain and reach each web server by name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with five routers in a ring. One router has a LAN with a root DNS server. Two other routers each have a LAN with a web server and its authoritative DNS server — one for research.org and one for example.net. A fourth router has a LAN with a local DNS server and two clients. The fifth router has a LAN with two more clients. Use IPv4. Write all routes by hand. The clients must find both domain names through the full DNS chain and reach each web server by name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 26 — Three Routers in a Line, Switches, Explicit Routes, IPv6

**Difficulty:** Medium

**Main concepts:** IPv6, linear topology, three routers, switches, explicit routes, no default routes

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab using IPv6 only. Put three routers in a line. Each router has one LAN with a switch and four PCs behind it. Write all IPv6 routes on every router. Do not use default routes. All twelve PCs must reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab using IPv6 only. Put three routers in a line. Each router has one LAN with a switch and four PCs behind it. Write all IPv6 routes on every router. Do not use default routes. All twelve PCs must reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 27 — Five-Router Tree, Main Server, DNS Chain, Web Server, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, tree topology, five routers, main server, DNS chain, web server, combined services

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with five routers in a tree. The root router connects to two second-level routers. Each second-level router connects to one leaf router. The root router has a LAN with a main server. One leaf router has a LAN with a web server for company.test, its authoritative DNS server and a root DNS server. The other leaf router has a LAN with a client and a local DNS server. Each second-level router has a LAN with two more clients. Use IPv4. Write all routes by hand. Every client must reach the main server by IP. The client with the local DNS must also find company.test through DNS and open the web page by name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with five routers in a tree. The root router connects to two second-level routers. Each second-level router connects to one leaf router. The root router has a LAN with a main server. One leaf router has a LAN with a web server for company.test, its authoritative DNS server and a root DNS server. The other leaf router has a LAN with a client and a local DNS server. Each second-level router has a LAN with two more clients. Use IPv4. Write all routes by hand. Every client must reach the main server by IP. The client with the local DNS must also find company.test through DNS and open the web page by name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 28 — Dual-Stack Ring, Five Routers, Core and Edge Routing Mix

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, ring topology, five routers, core routers, default routes on edges

**Version A**

```text
Generate a detailed prompt file for this request: Make a lab with five routers in a ring. Each router has one LAN with two PCs. Use both IPv4 and IPv6. Pick two routers as core routers with full explicit routes to every network. The other three routers should use a default route toward the closest core router. Write all routes by hand for both protocols. All PCs must reach all other PCs on both IPv4 and IPv6.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Make a lab with five routers in a ring. Each router has one LAN with two PCs. Use both IPv4 and IPv6. Pick two routers as core routers with full explicit routes to every network. The other three routers should use a default route toward the closest core router. Write all routes by hand for both protocols. All PCs must reach all other PCs on both IPv4 and IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 29 — Asymmetric Tree, Five Routers, Uneven Branches, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, asymmetric tree, five routers, uneven branches, explicit routes

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with five routers in a lopsided tree. The root router connects to two child routers. The first child connects to two more routers below it. The second child has no children. The root router has a LAN with one PC. The first child has a LAN with two PCs. The two grandchild routers each have a LAN with three PCs. The second child has a LAN with two PCs. Use IPv4. Write every route by hand. No default routes. All PCs must reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with five routers in a lopsided tree. The root router connects to two child routers. The first child connects to two more routers below it. The second child has no children. The root router has a LAN with one PC. The first child has a LAN with two PCs. The two grandchild routers each have a LAN with three PCs. The second child has a LAN with two PCs. Use IPv4. Write every route by hand. No default routes. All PCs must reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 30 — IPv6 Partial Mesh, Five Routers, Web Server, Switches, Max Degree 3

**Difficulty:** Advanced

**Main concepts:** IPv6, partial mesh, five routers, web server, switches, connection limit

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab using IPv6 only with five routers in a partial mesh. No router connects to more than three others. One router has a LAN with a web server. Three routers each have a LAN with a switch and three clients behind the switch. One router just passes traffic and has no LAN. Write all IPv6 routes by hand. Do not use default routes. All clients must reach the web server.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab using IPv6 only with five routers in a partial mesh. No router connects to more than three others. One router has a LAN with a web server. Three routers each have a LAN with a switch and three clients behind the switch. One router just passes traffic and has no LAN. Write all IPv6 routes by hand. Do not use default routes. All clients must reach the web server.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 31 — Star-of-Stars, Two Levels, Seven Routers, IPv4, Default Routes

**Difficulty:** Advanced

**Main concepts:** IPv4, two-level star, seven routers, core router, distribution routers, access routers, default routes

**Version A**

```text
Generate a detailed prompt file for this request: Make a lab with one core router, two distribution routers and four access routers. The core router connects to both distribution routers. Each distribution router connects to two access routers. Each access router has one LAN with three PCs. The core and distribution routers have no LANs. Use IPv4. Access routers should use a default route toward their distribution router. Distribution routers should use a default route toward the core router and explicit routes for their access LANs. The core router must have explicit routes to all access LANs. All PCs must reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Make a lab with one core router, two distribution routers and four access routers. The core router connects to both distribution routers. Each distribution router connects to two access routers. Each access router has one LAN with three PCs. The core and distribution routers have no LANs. Use IPv4. Access routers should use a default route toward their distribution router. Distribution routers should use a default route toward the core router and explicit routes for their access LANs. The core router must have explicit routes to all access LANs. All PCs must reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 32 — Dual-Stack Line, Five Routers, Central Server and Web Server

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, linear topology, five routers, central server, web server, no default routes

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with five routers in a line. The first router has a LAN with a central server. The last router has a LAN with a web server. The three middle routers each have a LAN with two clients. Use both IPv4 and IPv6 on everything. Write all routes by hand for both protocols. Do not use default routes. Every client must reach both the central server and the web server on both IPv4 and IPv6.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with five routers in a line. The first router has a LAN with a central server. The last router has a LAN with a web server. The three middle routers each have a LAN with two clients. Use both IPv4 and IPv6 on everything. Write all routes by hand for both protocols. Do not use default routes. Every client must reach both the central server and the web server on both IPv4 and IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 33 — IPv4 Ring, Four Routers, Two Local DNS Servers

**Difficulty:** Medium

**Main concepts:** IPv4, ring topology, four routers, two local DNS servers, web server, domain name

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with four routers in a ring. One router has a LAN with a web server for network.lab. Two other routers each have a LAN with clients and a local DNS server. The fourth router has a LAN with two clients that use one of the existing DNS servers. Both DNS servers must know the web server address. Use IPv4. Write all routes by hand. All clients must access network.lab by domain name, each using their own local DNS server.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with four routers in a ring. One router has a LAN with a web server for network.lab. Two other routers each have a LAN with clients and a local DNS server. The fourth router has a LAN with two clients that use one of the existing DNS servers. Both DNS servers must know the web server address. Use IPv4. Write all routes by hand. All clients must access network.lab by domain name, each using their own local DNS server.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 34 — IPv6 Tree, Four Routers, Central Server and DNS

**Difficulty:** Medium

**Main concepts:** IPv6, tree topology, four routers, central server, local DNS, domain name, default routes

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab using IPv6 only with four routers in a tree. The root router connects to three child routers. The root router has a LAN with a central server for the domain service.local and a local DNS server. Each child router has one LAN with three clients. Write all IPv6 routes by hand. The DNS server must know the central server address. All clients must reach the central server by domain name. Child routers can use a default route.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab using IPv6 only with four routers in a tree. The root router connects to three child routers. The root router has a LAN with a central server for the domain service.local and a local DNS server. Each child router has one LAN with three clients. Write all IPv6 routes by hand. The DNS server must know the central server address. All clients must reach the central server by domain name. Child routers can use a default route.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 35 — Five Routers, Partial Mesh, Two Web Servers, Selective Client Access, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, partial mesh, five routers, two web servers, selective access, connection limit

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with five routers in a partial mesh. No router connects to more than three others. One router has a LAN with a web server for kathara.org. Another has a LAN with a web server for example.net. Two routers each have a LAN with three clients. The fifth router just passes traffic. Use IPv4. Write all routes by hand. Clients in the first LAN must reach only kathara.org. Clients in the second LAN must reach only example.net. No client needs access to the other web server.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with five routers in a partial mesh. No router connects to more than three others. One router has a LAN with a web server for kathara.org. Another has a LAN with a web server for example.net. Two routers each have a LAN with three clients. The fifth router just passes traffic. Use IPv4. Write all routes by hand. Clients in the first LAN must reach only kathara.org. Clients in the second LAN must reach only example.net. No client needs access to the other web server.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 36 — Dual-Stack Ring, Six Routers, Full DNS Chain, Web Server

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, ring topology, six routers, root DNS, TLD DNS, authoritative DNS, local DNS, web server

**Version A**

```text
Generate a detailed prompt file for this request: Make a lab with six routers in a ring. Use both IPv4 and IPv6. One router has a LAN with a root DNS server. Another has a LAN with a DNS server for the edu domain. A third has a LAN with an authoritative DNS server for university.edu and a web server for university.edu. A fourth has a LAN with a local DNS server and two clients. The other two routers each have a LAN with two more clients. Write all routes by hand for both protocols. All clients must find university.edu through the DNS chain and open the web page by name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Make a lab with six routers in a ring. Use both IPv4 and IPv6. One router has a LAN with a root DNS server. Another has a LAN with a DNS server for the edu domain. A third has a LAN with an authoritative DNS server for university.edu and a web server for university.edu. A fourth has a LAN with a local DNS server and two clients. The other two routers each have a LAN with two more clients. Write all routes by hand for both protocols. All clients must find university.edu through the DNS chain and open the web page by name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 37 — Three Routers in a Line, Two Switches, Eight PCs, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, linear topology, three routers, two switches, eight PCs, transit router, default routes

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with three routers in a line. The first router has a LAN with a switch and four PCs. The last router has a LAN with a switch and four PCs. The middle router connects to both end routers but has no LAN. Use IPv4. Write all routes by hand. The middle router must not use default routes. The end routers can use a default route. All eight PCs must reach each other.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with three routers in a line. The first router has a LAN with a switch and four PCs. The last router has a LAN with a switch and four PCs. The middle router connects to both end routers but has no LAN. Use IPv4. Write all routes by hand. The middle router must not use default routes. The end routers can use a default route. All eight PCs must reach each other.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 38 — IPv6 Partial Mesh, Five Routers, DNS and Central Server

**Difficulty:** Advanced

**Main concepts:** IPv6, partial mesh, five routers, root DNS, authoritative DNS, local DNS, central server, domain name

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab using IPv6 only with five routers in a partial mesh. No router connects to more than three others. One router has a LAN with a root DNS server and an authoritative DNS server for research.org. Another has a LAN with a central server hosting research.org. A third has a LAN with a local DNS server and two clients. The last two routers each have a LAN with two more clients. Write all IPv6 routes by hand. The clients with the local DNS server must find research.org through DNS and reach the central server by name. Other clients must reach the central server by IP address.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab using IPv6 only with five routers in a partial mesh. No router connects to more than three others. One router has a LAN with a root DNS server and an authoritative DNS server for research.org. Another has a LAN with a central server hosting research.org. A third has a LAN with a local DNS server and two clients. The last two routers each have a LAN with two more clients. Write all IPv6 routes by hand. The clients with the local DNS server must find research.org through DNS and reach the central server by name. Other clients must reach the central server by IP address.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 39 — Dual-Stack Five-Router Star, Web Server, Central Server, DNS

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, star topology, five routers, web server, central server, local DNS, combined services

**Version A**

```text
Generate a detailed prompt file for this request: Make a lab with one central router and four edge routers. The central router has a LAN with a web server for service.local and a central server. One edge router has a LAN with a local DNS server and three clients. The other three edge routers each have a LAN with two clients. Use both IPv4 and IPv6. Edge routers should use a default route to the central router. The central router needs explicit routes. The DNS server must know the web server address. The clients with the DNS server must reach the web server by name. All clients must reach the central server by IP on both protocols.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Make a lab with one central router and four edge routers. The central router has a LAN with a web server for service.local and a central server. One edge router has a LAN with a local DNS server and three clients. The other three edge routers each have a LAN with two clients. Use both IPv4 and IPv6. Edge routers should use a default route to the central router. The central router needs explicit routes. The DNS server must know the web server address. The clients with the DNS server must reach the web server by name. All clients must reach the central server by IP on both protocols.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 40 — Large Dual-Stack Lab: Seven Routers, DNS Chain, Two Web Servers, Central Server

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, seven routers, partial mesh, root DNS, TLD DNS, two authoritative DNS, two web servers, central server, local DNS

**Version A**

```text
Generate a detailed prompt file for this request: Build a large lab with seven routers in a partial mesh. No router connects to more than three others. Use both IPv4 and IPv6. One router has a LAN with a root DNS server. Another has a LAN with a DNS server for the test domain. Two routers each have a LAN with a web server and its authoritative DNS server — one for company.test and one for library.test. One router has a LAN with a central server. One router has a LAN with a local DNS server and three clients. The last router has a LAN with two more clients. Write all routes by hand for both protocols. The clients with the local DNS must find both company.test and library.test through DNS and open both web servers by name. All clients must also reach the central server by IP. Do not use default routes.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a large lab with seven routers in a partial mesh. No router connects to more than three others. Use both IPv4 and IPv6. One router has a LAN with a root DNS server. Another has a LAN with a DNS server for the test domain. Two routers each have a LAN with a web server and its authoritative DNS server — one for company.test and one for library.test. One router has a LAN with a central server. One router has a LAN with a local DNS server and three clients. The last router has a LAN with two more clients. Write all routes by hand for both protocols. The clients with the local DNS must find both company.test and library.test through DNS and open both web servers by name. All clients must also reach the central server by IP. Do not use default routes.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---
