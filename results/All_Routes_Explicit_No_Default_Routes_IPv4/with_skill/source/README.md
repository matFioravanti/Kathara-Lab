# Five-router IPv4 static-routing lab

This lab connects five routed LANs. R1 connects to R2 and R3; R2 and R3 each connect to R4; and R4 connects to R5. Every LAN has two PCs. Routers use only specific IPv4 static routes for every non-directly-connected subnet, with no default route configured on a router.

Start the lab with:

```sh
kathara lstart
```

For a quick end-to-end check, run `ping -c 2 10.10.5.11` from `pc1a`; then test additional PCs in the same way. All ten PCs should be mutually reachable.
