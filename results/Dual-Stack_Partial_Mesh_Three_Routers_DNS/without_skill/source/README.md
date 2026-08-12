# Dual-stack partial-mesh DNS laboratory

R1, R2, and R3 have direct dual-stack links in a triangle. Each router also has its own IPv4/IPv6 LAN. `DNS` is authoritative for `company.test`; the name has A record `192.168.2.80` and AAAA record `2001:db8:2::80`. `WEB` serves HTTP on both families.

After starting the lab, use these checks on `CLIENT`:

```sh
getent ahostsv4 company.test
getent ahostsv6 company.test
curl -4 http://company.test/
curl -6 http://company.test/
```
