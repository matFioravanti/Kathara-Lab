# Five Routers, Static Routing, Hierarchical DNS, and Web Server

This lab connects a client to `kathara.org` through five statically routed routers. The client uses `localdns`, a recursive resolver with a root hint. `rootdns` delegates the `org` top-level domain to `orgdns`, which is authoritative for `kathara.org`; the resulting address is the Apache server `web`.

Start the laboratory from this directory:

```sh
kathara lstart
```

Quick validation from the client:

```sh
kathara exec client -- ping -c 2 kathara.org
kathara exec client -- curl http://kathara.org
```

The five routers form the path `r1 - r2 - r3 - r4 - r5`. Router `r2` additionally connects the local DNS LAN, and router `r3` additionally connects the root DNS LAN, so no router has a degree greater than three.
