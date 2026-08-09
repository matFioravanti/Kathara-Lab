# Static routing with hierarchical DNS

This laboratory uses five statically routed routers. The client asks the local recursive DNS server for `kathara.org`; that server follows its root hint to the root DNS server, receives the referral for the `org` zone, and obtains the final address from the authoritative `org` DNS server. The resulting address points to the Apache web server.

Start the lab with:

```sh
kathara lstart
```

From `client`, verify name resolution and HTTP access:

```sh
ping -c 2 kathara.org
curl http://kathara.org/
```

Addressing uses the `10.10.0.0/16` private range. Routers `r2`, `r3`, and `r4` each have exactly three interfaces; `r1` and `r5` have two.
