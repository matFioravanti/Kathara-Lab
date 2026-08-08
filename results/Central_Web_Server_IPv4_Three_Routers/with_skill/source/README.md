# IPv4 Static Routing and HTTP

This lab demonstrates IPv4 connectivity between two clients and an Apache web server through three routers arranged in a line. Every non-connected network is reached with a manually configured static route; no dynamic routing protocol is used.

## Topology and addressing

| Device | Interface | IPv4 address | Connected network |
| --- | --- | --- | --- |
| client1 | eth0 | 192.168.10.10/24 | left LAN |
| client2 | eth0 | 192.168.10.11/24 | left LAN |
| router1 | eth0 | 192.168.10.1/24 | left LAN |
| router1 | eth1 | 10.0.12.1/30 | router1-router2 |
| router2 | eth0 | 10.0.12.2/30 | router1-router2 |
| router2 | eth1 | 10.0.23.1/30 | router2-router3 |
| router3 | eth0 | 10.0.23.2/30 | router2-router3 |
| router3 | eth1 | 192.168.30.1/24 | server LAN |
| webserver | eth0 | 192.168.30.10/24 | server LAN |

## Run and verify

Start the lab from this directory:

```sh
kathara lstart
```

From either client, verify IP reachability and the HTTP application:

```sh
kathara exec client1 -- ping -c 2 192.168.30.10
kathara exec client1 -- curl http://192.168.30.10/
```
