# Authoritative DNS for Multiple Domains (IPv4)

This lab demonstrates a local DNS resolver that forwards `university.edu` and `company.test` queries to their respective authoritative BIND servers over a statically routed IPv4 network. The two clients use the local DNS server and can access both Apache web servers by name.

Start the lab with:

```bash
kathara lstart
```

From either client, verify name resolution and HTTP reachability:

```bash
dig www.university.edu
dig www.company.test
curl http://www.university.edu
curl http://www.company.test
```
