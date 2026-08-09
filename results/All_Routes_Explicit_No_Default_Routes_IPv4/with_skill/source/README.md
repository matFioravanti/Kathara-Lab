# Five-router explicit IPv4 static routing

This lab has five routers in a redundant R1--R4 core and one two-PC LAN behind each router. Every router has a specific static route for each subnet that is not directly attached; router startup files contain no default route. IPv6 is disabled on every device.

Start the lab from this directory with:

```sh
kathara lstart
```

As a quick end-to-end check, run `ping -c 2 10.1.5.11` from `pc1a`; it should reach `pc5b`. Other PC addresses are `10.1.N.10` and `10.1.N.11` for LAN `N` (1 through 5).
