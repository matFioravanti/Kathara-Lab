# Three-Router IPv4 Static Routing Lab

This lab connects two clients on a left LAN to an Apache HTTP server on a right LAN through three routers in a line. IPv4 forwarding and all non-connected routes are configured statically; no dynamic routing protocol is used.

## Topology and addressing

| Device | Interface | Address | Connected network |
|---|---|---|---|
| client1 | eth0 | 192.168.10.10/24 | left LAN |
| client2 | eth0 | 192.168.10.11/24 | left LAN |
| router1 | eth0 | 192.168.10.1/24 | left LAN |
| router1 | eth1 | 10.0.12.1/30 | router1-router2 transit |
| router2 | eth0 | 10.0.12.2/30 | router1-router2 transit |
| router2 | eth1 | 10.0.23.1/30 | router2-router3 transit |
| router3 | eth0 | 10.0.23.2/30 | router2-router3 transit |
| router3 | eth1 | 192.168.30.1/24 | right LAN |
| webserver | eth0 | 192.168.30.10/24 | right LAN |

## Run and test

Start the laboratory from this directory:

```sh
kathara lstart
```

From `client1`, verify end-to-end HTTP access by IP address:

```sh
kathara exec client1 -- curl http://192.168.30.10/
```

`client2` can run the same command. The response contains the heading `Static IPv4 HTTP Service`.
