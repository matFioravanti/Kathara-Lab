# Kathara Lab Mini-Prompt Collection — Simple Natural Language

> **40 distinct scenarios** — each with Version A and Version B.
> All scenarios use static routing only. No dynamic protocols.

---

### Scenario 01 — Two Routers, Two LANs, IPv4

**Difficulty:** Easy

**Main concepts:** IPv4, static routing, two routers, two LANs, PCs

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with two routers. Each router connects to one LAN. Each LAN has two PCs. Connect the two routers with a direct link. Use IPv4 only. Write the routes manually on each router. All PCs must be able to ping each other.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with two routers. Each router connects to one LAN. Each LAN has two PCs. Connect the two routers with a direct link. Use IPv4 only. Write the routes manually on each router. All PCs must be able to ping each other.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 02 — Three Routers in a Line, IPv4

**Difficulty:** Easy

**Main concepts:** IPv4, static routing, linear topology, three routers, three LANs

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with three routers placed in a line. The first router connects to the second, and the second connects to the third. Each router has one LAN with two PCs. Use IPv4. Write all routes by hand. No router can connect to more than two other routers. Every PC must reach every other PC.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with three routers placed in a line. The first router connects to the second, and the second connects to the third. Each router has one LAN with two PCs. Use IPv4. Write all routes by hand. No router can connect to more than two other routers. Every PC must reach every other PC.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 03 — One Router with Four LANs, IPv4

**Difficulty:** Easy

**Main concepts:** IPv4, star topology, one router, four LANs, switches, PCs

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with one central router connected to four different LANs. Each LAN has a switch and three PCs. Use IPv4 only. Set addresses on all interfaces manually. Every PC in every LAN must be able to reach every other PC through the router.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with one central router connected to four different LANs. Each LAN has a switch and three PCs. Use IPv4 only. Set addresses on all interfaces manually. Every PC in every LAN must be able to reach every other PC through the router.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 04 — Simple IPv6 Lab, Two Routers

**Difficulty:** Easy

**Main concepts:** IPv6, static routing, two routers, two LANs, PCs

**Version A**

```text
Generate a detailed prompt file for this request: Build a small lab that uses IPv6 only. Add two routers connected by a direct link. Each router serves one LAN with three PCs. Assign all IPv6 addresses by hand. Write static routes on both routers. PCs on both LANs must be able to reach each other.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a small lab that uses IPv6 only. Add two routers connected by a direct link. Each router serves one LAN with three PCs. Assign all IPv6 addresses by hand. Write static routes on both routers. PCs on both LANs must be able to reach each other.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 05 — Dual-Stack Lab, Two Routers

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, static routing, two routers

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab where every device runs both IPv4 and IPv6 at the same time. Use two routers connected by a direct link. Each router has one LAN with two PCs. Assign both an IPv4 and an IPv6 address to every interface. Write all routes manually for both address families. PCs must reach each other using both IPv4 and IPv6.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab where every device runs both IPv4 and IPv6 at the same time. Use two routers connected by a direct link. Each router has one LAN with two PCs. Assign both an IPv4 and an IPv6 address to every interface. Write all routes manually for both address families. PCs must reach each other using both IPv4 and IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 06 — Four Routers in a Ring, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, ring topology, four routers, static routing, default routes

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with four routers arranged in a ring. Each router connects to the next one, and the last one connects back to the first. Each router also connects to one LAN with two PCs. Use IPv4. Write routes manually on every router. Edge routers can use a default route to keep their tables short. All PCs must be able to reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with four routers arranged in a ring. Each router connects to the next one, and the last one connects back to the first. Each router also connects to one LAN with two PCs. Use IPv4. Write routes manually on every router. Edge routers can use a default route to keep their tables short. All PCs must be able to reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 07 — Tree of Routers, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, tree topology, three routers, static routing, four LANs

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab where routers are connected as a tree. One root router connects to two other routers. Each of the two child routers connects to two LANs, each with two PCs. The root router also connects to its own LAN with two PCs. Use IPv4. Write all routes by hand. Every PC must reach every other PC.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab where routers are connected as a tree. One root router connects to two other routers. Each of the two child routers connects to two LANs, each with two PCs. The root router also connects to its own LAN with two PCs. Use IPv4. Write all routes by hand. Every PC must reach every other PC.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 08 — Switch with Many PCs, IPv4

**Difficulty:** Easy

**Main concepts:** IPv4, Ethernet switch, single LAN, five PCs, one router

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with one router connected to a switch. The switch connects to five PCs. Use IPv4 only. All PCs must be in the same LAN and must be able to ping each other through the switch. The router connects this LAN to a second small LAN with one PC. Both LANs must be able to communicate. Write all routes manually.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with one router connected to a switch. The switch connects to five PCs. Use IPv4 only. All PCs must be in the same LAN and must be able to ping each other through the switch. The router connects this LAN to a second small LAN with one PC. Both LANs must be able to communicate. Write all routes manually.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 09 — Central Web Server, IPv4

**Difficulty:** Easy

**Main concepts:** IPv4, web server, static routing, two routers, clients

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with a central web server that must be reachable from all clients. Use two routers connected by a direct link. One router connects to a LAN with three clients. The other router connects to the web server. Use IPv4. Write all routes manually. Every client must be able to open the web server using its IP address.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with a central web server that must be reachable from all clients. Use two routers connected by a direct link. One router connects to a LAN with three clients. The other router connects to the web server. Use IPv4. Write all routes manually. Every client must be able to open the web server using its IP address.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 10 — Local DNS Server and Web Server, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, local DNS server, web server, static routing, domain name

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with two routers. One router connects to a LAN where a client and a local DNS server live. The other router connects to a LAN with a web server for the domain example.net. Use IPv4. Write all routes manually. The client must use the local DNS server to find the web server by name and then open the web page.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with two routers. One router connects to a LAN where a client and a local DNS server live. The other router connects to a LAN with a web server for the domain example.net. Use IPv4. Write all routes manually. The client must use the local DNS server to find the web server by name and then open the web page.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 11 — Root, TLD and Local DNS, Full Resolution Chain, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, root DNS server, TLD DNS server, local DNS server, web server, static routing

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab where DNS resolution goes through three levels. Add a root DNS server, a DNS server for the org domain and a local DNS server for the client. Add a web server for research.org in a separate network. Use three routers to connect all networks. Use IPv4. Write all routes manually. The client must ask its local DNS server, which must talk to the root and then the org server, to find the web server by name. The client must then open the web page.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab where DNS resolution goes through three levels. Add a root DNS server, a DNS server for the org domain and a local DNS server for the client. Add a web server for research.org in a separate network. Use three routers to connect all networks. Use IPv4. Write all routes manually. The client must ask its local DNS server, which must talk to the root and then the org server, to find the web server by name. The client must then open the web page.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 12 — Two Web Servers, Two Domains, One DNS Chain, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, two web servers, two authoritative DNS servers, local DNS server, root DNS server

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with two web servers in different networks. One server hosts campus.net and the other hosts library.test. Add a root DNS server, an authoritative DNS server for each domain and a local DNS server for the clients. Use four routers. Use IPv4 and write all routes manually. Two clients must each open a different web server by domain name. DNS must work correctly for both names.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with two web servers in different networks. One server hosts campus.net and the other hosts library.test. Add a root DNS server, an authoritative DNS server for each domain and a local DNS server for the clients. Use four routers. Use IPv4 and write all routes manually. Two clients must each open a different web server by domain name. DNS must work correctly for both names.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 13 — Five Routers, Partial Mesh, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, partial mesh, five routers, static routing, connection limit

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with five routers connected as a partial mesh. No router can connect to more than three other routers. Each router has one LAN with two PCs. Use IPv4. Write all routes by hand. Every PC must be able to reach every other PC.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with five routers connected as a partial mesh. No router can connect to more than three other routers. Each router has one LAN with two PCs. Use IPv4. Write all routes by hand. Every PC must be able to reach every other PC.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 14 — Edge Routers with Default Routes, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, default routes, edge routers, central router, static routing

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with one central router and three edge routers. Each edge router connects to the central router and to one LAN with two PCs. Use IPv4. The edge routers must use a default route pointing to the central router. The central router must have explicit routes to all three edge LANs. All PCs must reach each other.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with one central router and three edge routers. Each edge router connects to the central router and to one LAN with two PCs. Use IPv4. The edge routers must use a default route pointing to the central router. The central router must have explicit routes to all three edge LANs. All PCs must reach each other.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 15 — IPv6 Ring, Four Routers

**Difficulty:** Medium

**Main concepts:** IPv6, ring topology, four routers, static routing, four LANs

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with four routers arranged in a ring. Each router connects to the next one, and the last connects back to the first. Each router also has one LAN with two PCs. Use IPv6 only. Write all routes manually. All PCs must be able to reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with four routers arranged in a ring. Each router connects to the next one, and the last connects back to the first. Each router also has one LAN with two PCs. Use IPv6 only. Write all routes manually. All PCs must be able to reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 16 — Dual-Stack Tree, Three Routers

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, tree topology, three routers, static routing

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with three routers in a tree. One root router connects to two other routers. Each child router has one LAN with two PCs. The root router has its own LAN with one PC. Run both IPv4 and IPv6 on all devices. Write all routes by hand for both address families. All PCs must reach each other on both protocols.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with three routers in a tree. One root router connects to two other routers. Each child router has one LAN with two PCs. The root router has its own LAN with one PC. Run both IPv4 and IPv6 on all devices. Write all routes by hand for both address families. All PCs must reach each other on both protocols.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 17 — Central Server Reachable from All LANs, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, central server, three routers, static routing, multiple LANs

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab where a central server must be reached from every LAN. Use three routers. The central server sits in a dedicated network connected to one of the routers. Each router also connects to one LAN with two clients. Use IPv4. Write all routes manually. Every client must be able to connect to the central server.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab where a central server must be reached from every LAN. Use three routers. The central server sits in a dedicated network connected to one of the routers. Each router also connects to one LAN with two clients. Use IPv4. Write all routes manually. Every client must be able to connect to the central server.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 18 — One Switch, Many PCs, No Router, IPv4

**Difficulty:** Easy

**Main concepts:** IPv4, Ethernet switch, single LAN, six PCs

**Version A**

```text
Generate a detailed prompt file for this request: Build a simple lab with one switch and six PCs. All PCs connect to the switch and must be in the same LAN. Use IPv4. Assign addresses manually to every PC. All PCs must be able to ping each other through the switch. No router is needed.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a simple lab with one switch and six PCs. All PCs connect to the switch and must be in the same LAN. Use IPv4. Assign addresses manually to every PC. All PCs must be able to ping each other through the switch. No router is needed.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 19 — DNS and Web Server Over IPv6

**Difficulty:** Advanced

**Main concepts:** IPv6, DNS server, web server, static routing, domain name

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab that runs on IPv6 only. Use three routers. Put a local DNS server and a client in one LAN. Put a web server for university.edu in another LAN. Put a root DNS server and a DNS server for the edu domain in a third LAN. Write all IPv6 routes by hand. The client must find university.edu through DNS and open the web page. Everything must run on IPv6 only.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab that runs on IPv6 only. Use three routers. Put a local DNS server and a client in one LAN. Put a web server for university.edu in another LAN. Put a root DNS server and a DNS server for the edu domain in a third LAN. Write all IPv6 routes by hand. The client must find university.edu through DNS and open the web page. Everything must run on IPv6 only.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 20 — Five Routers in a Line, IPv4, Explicit Routes Only

**Difficulty:** Advanced

**Main concepts:** IPv4, linear topology, five routers, explicit static routes, five LANs

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with five routers connected one after the other in a line. Each router has one LAN with two PCs. Use IPv4. Every router must have a complete routing table with an explicit route to every network in the lab. Do not use default routes anywhere. All PCs must reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with five routers connected one after the other in a line. Each router has one LAN with two PCs. Use IPv4. Every router must have a complete routing table with an explicit route to every network in the lab. Do not use default routes anywhere. All PCs must reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 21 — Dual-Stack DNS and Web Server

**Difficulty:** Advanced

**Main concepts:** dual-stack, IPv4, IPv6, DNS, web server, static routing

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab where devices run both IPv4 and IPv6. Use three routers. Add a local DNS server and a client in one LAN. Add a web server for training.lab in another LAN. The DNS server must know the address of the web server in both IPv4 and IPv6. Write all routes manually for both address families. The client must open training.lab using the domain name. Both address families must work.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab where devices run both IPv4 and IPv6. Use three routers. Add a local DNS server and a client in one LAN. Add a web server for training.lab in another LAN. The DNS server must know the address of the web server in both IPv4 and IPv6. Write all routes manually for both address families. The client must open training.lab using the domain name. Both address families must work.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 22 — Two Switches, Two LANs, One Router, IPv4

**Difficulty:** Easy

**Main concepts:** IPv4, two switches, two LANs, one router, PCs

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with one router and two switches. Each switch connects to the router and to three PCs, forming a separate LAN. Use IPv4 only. Write all routes manually. PCs in both LANs must be able to ping each other through the router.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with one router and two switches. Each switch connects to the router and to three PCs, forming a separate LAN. Use IPv4 only. Write all routes manually. PCs in both LANs must be able to ping each other through the router.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 23 — Partial Mesh with Connection Limit, IPv6

**Difficulty:** Advanced

**Main concepts:** IPv6, partial mesh, four routers, connection limit, static routing

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with four routers using IPv6 only. Connect them in a partial mesh where no router can connect to more than two other routers. Each router has one LAN with two PCs. Write all routes manually. All PCs must be able to reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with four routers using IPv6 only. Connect them in a partial mesh where no router can connect to more than two other routers. Each router has one LAN with two PCs. Write all routes manually. All PCs must be able to reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 24 — Authoritative DNS for Two Domains, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, two authoritative DNS servers, root DNS server, local DNS server, two web servers

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with a root DNS server, two authoritative DNS servers and a local DNS server. One authoritative server handles kathara.org and the other handles service.local. Add a web server for each domain in a separate network. Use four routers to connect everything. Use IPv4 and write all routes by hand. Two clients must each open a different web server by domain name. DNS must resolve both names correctly.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with a root DNS server, two authoritative DNS servers and a local DNS server. One authoritative server handles kathara.org and the other handles service.local. Add a web server for each domain in a separate network. Use four routers to connect everything. Use IPv4 and write all routes by hand. Two clients must each open a different web server by domain name. DNS must resolve both names correctly.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 25 — One Router, Three LANs, Default Routes on PCs, IPv4

**Difficulty:** Easy

**Main concepts:** IPv4, one router, three LANs, default routes, static routing

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with one router that connects to three different LANs. Each LAN has two PCs. Use IPv4 only. Each PC must have a default route pointing to the router. The router must have a route for each LAN. All PCs in all LANs must reach each other through the router.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with one router that connects to three different LANs. Each LAN has two PCs. Use IPv4 only. Each PC must have a default route pointing to the router. The router must have a route for each LAN. All PCs in all LANs must reach each other through the router.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 26 — Web Server Reachable by Name, Three Routers, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, web server, local DNS server, three routers, domain name, static routing

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with three routers. One router connects to a LAN with a client and a local DNS server. Another router connects to a LAN with a web server for network.lab. The third router sits between the other two. Use IPv4. Write all routes manually. The local DNS server must know the address of the web server. The client must open network.lab by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with three routers. One router connects to a LAN with a client and a local DNS server. Another router connects to a LAN with a web server for network.lab. The third router sits between the other two. Use IPv4. Write all routes manually. The local DNS server must know the address of the web server. The client must open network.lab by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 27 — IPv4 Star with Web Server at Centre

**Difficulty:** Medium

**Main concepts:** IPv4, star topology, central web server, four edge routers, default routes

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with a central router and four edge routers. Each edge router connects only to the central router and to one LAN with two clients. The web server is in a network connected to the central router. Use IPv4. Edge routers must use a default route to reach everything. The central router must have explicit routes to all four edge LANs. All clients must reach the web server by its IP address.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with a central router and four edge routers. Each edge router connects only to the central router and to one LAN with two clients. The web server is in a network connected to the central router. Use IPv4. Edge routers must use a default route to reach everything. The central router must have explicit routes to all four edge LANs. All clients must reach the web server by its IP address.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 28 — IPv6 Tree, DNS and Web Server

**Difficulty:** Advanced

**Main concepts:** IPv6, tree topology, DNS, web server, static routing, three routers

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab using IPv6 only. Arrange three routers in a tree. One root router connects to two child routers. One child router connects to a LAN with a client and a local DNS server. The other child router connects to a LAN with a web server for company.test. The root router connects to a LAN with the root DNS server and the DNS server for the test domain. Write all IPv6 routes manually. The client must find company.test through DNS and open the web page.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab using IPv6 only. Arrange three routers in a tree. One root router connects to two child routers. One child router connects to a LAN with a client and a local DNS server. The other child router connects to a LAN with a web server for company.test. The root router connects to a LAN with the root DNS server and the DNS server for the test domain. Write all IPv6 routes manually. The client must find company.test through DNS and open the web page.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 29 — Six Routers, Partial Mesh, IPv4, Explicit Routes

**Difficulty:** Advanced

**Main concepts:** IPv4, partial mesh, six routers, explicit static routes, connection limit

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with six routers connected in a partial mesh. No router can connect to more than three other routers. Each router has one LAN with two PCs. Use IPv4. Write a complete routing table on every router. Do not use default routes anywhere. All PCs must reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with six routers connected in a partial mesh. No router can connect to more than three other routers. Each router has one LAN with two PCs. Use IPv4. Write a complete routing table on every router. Do not use default routes anywhere. All PCs must reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 30 — Dual-Stack Central Server, Three Routers

**Difficulty:** Medium

**Main concepts:** dual-stack, IPv4, IPv6, central server, three routers, static routing

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with three routers. A central server is connected to one of the routers. Each router also has one LAN with two clients. Run both IPv4 and IPv6 on every device. Write all routes by hand for both protocols. Every client must reach the central server using both IPv4 and IPv6.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with three routers. A central server is connected to one of the routers. Each router also has one LAN with two clients. Run both IPv4 and IPv6 on every device. Write all routes by hand for both protocols. Every client must reach the central server using both IPv4 and IPv6.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 31 — Two LANs with Switches, IPv6, Two Routers

**Difficulty:** Easy

**Main concepts:** IPv6, two switches, two routers, two LANs, PCs

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with two separate LANs. Each LAN has a switch and three PCs. The two LANs are connected by a router on each side and a point-to-point link between the routers. Use IPv6 only. Write all addresses and routes by hand. PCs in both LANs must reach each other.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with two separate LANs. Each LAN has a switch and three PCs. The two LANs are connected by a router on each side and a point-to-point link between the routers. Use IPv6 only. Write all addresses and routes by hand. PCs in both LANs must reach each other.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 32 — DNS Full Chain Plus Two Clients, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, root DNS server, TLD DNS server, authoritative DNS server, local DNS server, two clients, web server

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab with a full DNS chain. Add a root DNS server, a DNS server for the net domain, an authoritative DNS server for campus.net and a local DNS server. Put two clients in one LAN with the local DNS server. Put the web server for campus.net in another LAN. Use four routers to connect all networks. Use IPv4. Write all routes manually. Both clients must open campus.net by domain name. DNS must resolve the name through all three DNS levels.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab with a full DNS chain. Add a root DNS server, a DNS server for the net domain, an authoritative DNS server for campus.net and a local DNS server. Put two clients in one LAN with the local DNS server. Put the web server for campus.net in another LAN. Use four routers to connect all networks. Use IPv4. Write all routes manually. Both clients must open campus.net by domain name. DNS must resolve the name through all three DNS levels.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 33 — Routers in a Line, Edge Default Routes, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, linear topology, four routers, default routes on edge routers, static routing

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with four routers in a line. The two end routers are edge routers and must use a default route pointing inward. The two middle routers must have explicit routes to every network. Each router has one LAN with two PCs. Use IPv4. All PCs must reach all other PCs.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with four routers in a line. The two end routers are edge routers and must use a default route pointing inward. The two middle routers must have explicit routes to every network. Each router has one LAN with two PCs. Use IPv4. All PCs must reach all other PCs.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 34 — Client Reaches Web Server by Name, Dual-Stack DNS

**Difficulty:** Advanced

**Main concepts:** dual-stack, DNS, web server, static routing, domain name, IPv4, IPv6

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab where a client must open a web server by name using either IPv4 or IPv6. Add a local DNS server that knows both the IPv4 and IPv6 address of the web server for kathara.org. Use two routers. The client and local DNS server share one LAN. The web server is in another LAN. Use both IPv4 and IPv6 on all devices. Write all routes by hand. The client must open kathara.org by domain name.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab where a client must open a web server by name using either IPv4 or IPv6. Add a local DNS server that knows both the IPv4 and IPv6 address of the web server for kathara.org. Use two routers. The client and local DNS server share one LAN. The web server is in another LAN. Use both IPv4 and IPv6 on all devices. Write all routes by hand. The client must open kathara.org by domain name.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 35 — Two Routers, Explicit Routes Only, IPv6

**Difficulty:** Easy

**Main concepts:** IPv6, two routers, explicit static routes, two LANs, no default routes

**Version A**

```text
Generate a detailed prompt file for this request: Build a small lab with two routers using IPv6 only. Each router has one LAN with two PCs. Connect the routers with a direct link. Write an explicit route on each router for every network. Do not use default routes. All PCs must reach each other.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a small lab with two routers using IPv6 only. Each router has one LAN with two PCs. Connect the routers with a direct link. Write an explicit route on each router for every network. Do not use default routes. All PCs must reach each other.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 36 — Central Router, Five LANs, One Web Server, IPv4

**Difficulty:** Medium

**Main concepts:** IPv4, one central router, five LANs, web server, default routes on PCs

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with one central router connected to five LANs. One LAN contains a web server. The other four LANs each have two clients. Use IPv4. Each client must have a default route to the central router. The central router must have explicit routes to all five LANs. All clients must reach the web server by its IP address.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with one central router connected to five LANs. One LAN contains a web server. The other four LANs each have two clients. Use IPv4. Each client must have a default route to the central router. The central router must have explicit routes to all five LANs. All clients must reach the web server by its IP address.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 37 — Two Clients, Two Web Servers, Shared DNS, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, two web servers, two clients, local DNS server, root DNS, authoritative DNS servers

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab where two clients each need to reach a different web server by domain name. One web server hosts example.net and the other hosts research.org. Add a root DNS server, an authoritative DNS server for each domain and one shared local DNS server used by both clients. Use five routers to connect all networks. Use IPv4. Write all routes manually. Each client must open its own web server by domain name. DNS must work for both clients.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab where two clients each need to reach a different web server by domain name. One web server hosts example.net and the other hosts research.org. Add a root DNS server, an authoritative DNS server for each domain and one shared local DNS server used by both clients. Use five routers to connect all networks. Use IPv4. Write all routes manually. Each client must open its own web server by domain name. DNS must work for both clients.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 38 — Switches in Two LANs, IPv6, One Router

**Difficulty:** Easy

**Main concepts:** IPv6, switches, two LANs, one router, PCs

**Version A**

```text
Generate a detailed prompt file for this request: Create a lab with one router and two switches. Each switch connects to the router and to four PCs. Use IPv6 only. Assign all addresses manually. Write routes on the router for both LANs. Every PC must be able to reach every other PC through the router.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Create a lab with one router and two switches. Each switch connects to the router and to four PCs. Use IPv6 only. Assign all addresses manually. Write routes on the router for both LANs. Every PC must be able to reach every other PC through the router.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 39 — DNS, Web Server and Central Server Combined, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, DNS, web server, central server, static routing, four routers

**Version A**

```text
Generate a detailed prompt file for this request: Build a lab that has both a web server and a central server. The web server is for the domain service.local. Add a local DNS server and a root DNS server. The central server must be reachable from every LAN. Use four routers. Use IPv4 and write all routes by hand. Clients must open service.local by domain name and must also be able to connect to the central server. Both services must work at the same time.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a lab that has both a web server and a central server. The web server is for the domain service.local. Add a local DNS server and a root DNS server. The central server must be reachable from every LAN. Use four routers. Use IPv4 and write all routes by hand. Clients must open service.local by domain name and must also be able to connect to the central server. Both services must work at the same time.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---

### Scenario 40 — Large Lab: Six Routers, DNS Full Chain, Web Server, IPv4

**Difficulty:** Advanced

**Main concepts:** IPv4, six routers, partial mesh, root DNS, TLD DNS, authoritative DNS, local DNS, web server, static routing

**Version A**

```text
Generate a detailed prompt file for this request: Build a large lab with six routers connected in a partial mesh. No router can connect to more than three other routers. Add a full DNS chain: a root DNS server, a DNS server for the org domain, an authoritative DNS server for kathara.org and a local DNS server. Add a web server for kathara.org in its own network. Place clients in two different LANs, each with its own local DNS server. Use IPv4. Write all routes manually. Every client must open kathara.org by domain name through DNS. All networks must be reachable.

Do not inspect other directories in this workspace.
Do not generate lab files in this step.
```

**Version B**

```text
Generate a detailed prompt file for this request: Build a large lab with six routers connected in a partial mesh. No router can connect to more than three other routers. Add a full DNS chain: a root DNS server, a DNS server for the org domain, an authoritative DNS server for kathara.org and a local DNS server. Add a web server for kathara.org in its own network. Place clients in two different LANs, each with its own local DNS server. Use IPv4. Write all routes manually. Every client must open kathara.org by domain name through DNS. All networks must be reachable.

Use the Skill.md in the kathara-lab-creation folder.
Do not generate lab files in this step.
```

---
