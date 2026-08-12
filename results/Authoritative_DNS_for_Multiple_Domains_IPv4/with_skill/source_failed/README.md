# Authoritative DNS for Multiple Domains (IPv4)

This laboratory demonstrates a local recursive DNS server that conditionally forwards requests to separate authoritative BIND servers for `university.edu` and `company.test`. Four routers form a static-routed chain; R1's LAN contains two clients and the local DNS server, R2 and R3 host the authoritative DNS and HTTP services, and R4 terminates the router chain.

## Topology and addressing

| Network | Connected devices | IPv4 network |
| --- | --- | --- |
| R1 LAN | R1, client1, client2, localdns | 192.168.10.0/24 |
| R1--R2 | R1, R2 | 10.0.12.0/30 |
| R2 LAN | R2, auth_university, web_university | 192.168.20.0/24 |
| R2--R3 | R2, R3 | 10.0.23.0/30 |
| R3 LAN | R3, auth_company, web_company | 192.168.30.0/24 |
| R3--R4 | R3, R4 | 10.0.34.0/30 |

Start the lab from this directory with `kathara lstart`.

From either client, verify name resolution and HTTP reachability:

```sh
getent hosts www.university.edu
curl http://www.university.edu
getent hosts www.company.test
curl http://www.company.test
```

The local resolver at `192.168.10.53` forwards only the two requested domains: `university.edu` to `192.168.20.53`, and `company.test` to `192.168.30.53`.
