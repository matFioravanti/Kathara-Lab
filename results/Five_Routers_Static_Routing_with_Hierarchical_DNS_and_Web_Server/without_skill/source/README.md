# Five routers, static routing, and hierarchical DNS

The router graph is `r1--r2--r3--r4--r5`; no router has more than three interfaces. All router forwarding paths are configured with explicit static routes.

DNS resolution is hierarchical: the client asks `lns` (`10.0.2.10`), which forwards to the authoritative root server (`rootdns`, `10.0.3.10`). The root zone delegates `org` to `orgdns` (`10.0.4.10`), and `orgdns` is authoritative for `kathara.org`, whose address is `10.0.5.10`.

After starting the lab, validate from the client:

```sh
getent hosts kathara.org
curl http://kathara.org/
```
