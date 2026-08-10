# Static Routing and Hierarchical DNS

This Kathara lab has five routers.  R1--R2--R3 is the transit path, with R3 branching to R4 (the root/org DNS network) and R5 (the web-server network).  R3 has degree three; every other router has degree two.

All forwarding is configured using explicit static routes in each router's `startup` file.  The client (`10.0.1.10`) uses the local recursive DNS server at `10.0.1.53`.  That resolver starts from the root server (`10.0.4.53`), which delegates `org` to the separate authoritative org server (`10.0.4.54`).  `kathara.org` resolves to `10.0.5.10`, where an HTTP service listens on port 80.

After starting the lab, validate from `client`:

```sh
dig kathara.org
wget -qO- http://kathara.org/
```
