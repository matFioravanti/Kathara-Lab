# Five routers with static routing and hierarchical DNS

The routers form the chain-and-branch topology `r1--r2--r3--r5` with `r2--r4`; their router-only degrees are 1, 3, 2, 1, and 1 respectively. All routes are explicitly configured in each router startup script.

`root-dns` delegates `kathara.org` to the authoritative `org-dns`, which maps the name to the web server at `10.0.5.80`. `local-dns` is the recursive local resolver and starts from the included root-hints file. The client uses it at `10.0.5.53`, so `curl http://kathara.org` reaches the web server through the complete DNS hierarchy.
