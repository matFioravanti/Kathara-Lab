# Static-routing hierarchical-DNS lab

This lab connects a client to the `kathara.org` web server across five statically routed routers.  `localdns` is the client's recursive resolver; it starts resolution from `rootdns`, which delegates `org` to `orgdns`.  The authoritative `orgdns` server returns `kathara.org = 10.0.50.2`.

Start the lab with:

```sh
kathara lstart
```

From the client, validate the complete path with:

```sh
kathara exec client -- getent hosts kathara.org
kathara exec client -- curl http://kathara.org/
```

The routers form the transit path `r1 - r2 - r3 - r4 - r5`. Their maximum degree is three: `r1`, `r3`, and `r4` each also attach one service LAN.
