# Client reaches a web server by name with simple IPv4 DNS

This lab contains a client, an authoritative DNS server, two statically routed routers, and a web server.

## Addressing

| Node | Interface | IPv4 address | Purpose |
|---|---|---|---|
| client | eth0 | 192.168.10.10/24 | DNS client |
| dns | eth0 | 192.168.10.53/24 | Authoritative DNS for `service.local` |
| r1 | eth0 / eth1 | 192.168.10.1/24 / 10.0.0.1/30 | Client-LAN router |
| r2 | eth0 / eth1 | 10.0.0.2/30 / 192.168.20.1/24 | Server-LAN router |
| web | eth0 | 192.168.20.80/24 | HTTP server |

The DNS zone maps `service.local` and `www.service.local` to `192.168.20.80`. The client resolver is explicitly set to `192.168.10.53`. Every non-connected route is configured statically; no dynamic routing protocol is used.

## Start and verify

From this directory, start the lab with:

```sh
kathara lstart
```

After the startup scripts finish installing and starting services, run these commands on the client:

```sh
kathara connect client
dig @192.168.10.53 service.local A +short
getent ahostsv4 service.local
curl --fail http://service.local/
```

The DNS commands must return `192.168.20.80`, and `curl` must display the `service.local is reachable` page. Stop the lab with `kathara lclean`.
