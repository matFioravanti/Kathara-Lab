# Authoritative DNS for Multiple Domains (IPv4)

This lab demonstrates two clients using the local DNS resolver on the R1 LAN to resolve the authoritative `university.edu` and `company.test` zones.  All inter-router forwarding uses static IPv4 routes.

Start the lab with:

```sh
kathara lstart
```

From either client, confirm name resolution and HTTP connectivity:

```sh
dig www.university.edu
curl http://www.university.edu
dig www.company.test
curl http://www.company.test
```
