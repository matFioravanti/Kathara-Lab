# Dual-stack central-server star

Four routers form a star: `central` connects to `edge1`, `edge2`, and `edge3`. Each edge router serves two clients, while the central LAN contains `server`. IPv4 and IPv6 forwarding and static routing provide end-to-end reachability to the server.

Start the laboratory from this directory:

```sh
kathara lstart
```

For a quick dual-stack test from every edge client, run:

```sh
ping -c 2 10.0.10.10
ping -6 -c 2 fd00:0:10::10
```

The edge routers use static IPv4 and IPv6 default routes to `central`; `central` has explicit static routes to all three edge LANs.
