# Authoritative DNS and HTTP lab

This lab demonstrates a client using the local authoritative DNS server to resolve `service.local`, then retrieving its web page across two statically routed IPv4 LANs.

Start the laboratory from this directory with:

```sh
kathara lstart
```

From the client, verify name resolution and HTTP access with:

```sh
kathara exec client -- dig @192.168.10.53 service.local A +short
kathara exec client -- curl http://service.local/
```
