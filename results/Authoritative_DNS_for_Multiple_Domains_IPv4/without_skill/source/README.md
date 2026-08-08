# Authoritative DNS for Multiple Domains (IPv4)

Topology: `client1/client2 -- R1 -- R2 -- R3 -- R4`. R1, R2, and R3 each also attach to their own LAN. R4 intentionally has no end-user LAN.

| Service | Address | Name |
| --- | --- | --- |
| Local conditional resolver | 192.168.10.53 | forwards `university.edu` to 192.168.20.53 and `company.test` to 192.168.30.53 |
| University authoritative DNS / web | 192.168.20.53 / 192.168.20.80 | `university.edu` |
| Company authoritative DNS / web | 192.168.30.53 / 192.168.30.80 | `company.test` |

All interfaces, default gateways, and inter-router static routes are configured by the startup files. Both clients use `192.168.10.53` as their resolver.

After starting the lab, validate from either client:

```sh
getent hosts university.edu
getent hosts company.test
wget -qO- http://university.edu
wget -qO- http://company.test
```
