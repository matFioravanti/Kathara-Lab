# Five-router IPv4 static-routing lab

This laboratory contains five routers and ten PCs.  Each router serves one
two-PC LAN.  R1 connects to R2 and R3; R2 and R3 each connect to R4; R4
connects to R5.  IPv6 is disabled and every router has a specific static
route for each non-connected IPv4 subnet.  No router has a default route.

Start the lab from this directory with:

```sh
kathara lstart
```

For a quick end-to-end check, ping the farthest LAN host from `pc1a`:

```sh
kathara exec pc1a -- ping -c 2 10.10.5.12
```

The same addressing convention is used on every LAN: the router is `.1`,
and the PCs are `.11` and `.12`.
