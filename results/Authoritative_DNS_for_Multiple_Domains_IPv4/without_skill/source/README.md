# Authoritative DNS for Multiple Domains (IPv4)

This lab has four statically routed routers in a chain. `dns-local` is the resolver used by both clients. It conditionally forwards `university.edu` to `dns-university` and `company.test` to `dns-company`.

## Addressing

| Device | IPv4 address | Default gateway |
|---|---:|---:|
| client1 | 192.168.10.10/24 | 192.168.10.1 |
| client2 | 192.168.10.11/24 | 192.168.10.1 |
| dns-local | 192.168.10.53/24 | 192.168.10.1 |
| dns-university | 192.168.20.53/24 | 192.168.20.1 |
| web-university | 192.168.20.80/24 | 192.168.20.1 |
| dns-company | 192.168.30.53/24 | 192.168.30.1 |
| web-company | 192.168.30.80/24 | 192.168.30.1 |

Inter-router links are `10.0.12.0/30` (R1--R2), `10.0.23.0/30` (R2--R3), and `10.0.34.0/30` (R3--R4).

## Start and test

From this directory, start the lab with `kathara lstart`. On either client, use:

```sh
getent hosts www.university.edu
getent hosts www.company.test
wget -qO- http://www.university.edu
wget -qO- http://www.company.test
```

The expected addresses are `192.168.20.80` and `192.168.30.80`; each HTTP request returns a page identifying its domain.
