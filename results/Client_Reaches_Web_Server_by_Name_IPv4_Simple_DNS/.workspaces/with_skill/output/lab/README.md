# Authoritative DNS and HTTP lab

This lab uses two routers and static IPv4 routes to connect a client/DNS LAN to a web-server LAN. The DNS host is authoritative for `service.local` and returns the web server address `10.10.2.80`.

Start the laboratory from this directory:

```sh
kathara lstart
```

From the client, verify name resolution and HTTP access:

```sh
kathara exec client -- dig @10.10.1.53 service.local A
kathara exec client -- curl http://service.local
```

Addressing: client `10.10.1.10/24`, DNS `10.10.1.53/24`, R1 LAN/transit `10.10.1.1/24` and `10.10.12.1/30`, R2 transit/LAN `10.10.12.2/30` and `10.10.2.1/24`, web `10.10.2.80/24`.
