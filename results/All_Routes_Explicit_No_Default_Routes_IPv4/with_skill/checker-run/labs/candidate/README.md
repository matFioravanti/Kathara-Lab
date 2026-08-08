# Five-router IPv4 static-routing laboratory

This lab connects five router LANs through the topology R1--R2--R4--R5 and R1--R3--R4. Each LAN has two PCs. IPv4 forwarding is enabled on every router, and each router has individual static routes for every non-direct LAN and point-to-point subnet; no router has a default route.

Start the lab from this directory with:

```sh
kathara lstart
```

For a quick end-to-end test, run `ping -c 2 10.1.5.11` from PC11. To inspect the explicit routes on a router, run `ip route show` inside that router.
