# Hierarchical DNS with static routing

This lab uses five statically routed routers. `rootdns` is authoritative for the root zone and delegates `org` to `orgdns`; `localdns` performs recursive resolution for the client. The `org` zone maps `kathara.org` to the Apache server.

Start the lab with:

```sh
kathara lstart
```

From `client`, verify name resolution and web access:

```sh
ping -c 2 kathara.org
curl http://kathara.org/
```

The address plan is: client/local DNS `10.10.1.0/24`, organization DNS `10.10.3.0/24`, web server `10.10.4.0/24`, and root DNS `10.10.5.0/24`. Router transit links use `10.10.12.0/30`, `10.10.23.0/30`, `10.10.34.0/30`, and `10.10.45.0/30`.
