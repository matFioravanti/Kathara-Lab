# Dual-stack partial mesh with DNS

Three routers form a full triangle of inter-router links, with each router serving a separate LAN. R1's LAN contains a client and the authoritative DNS server; R2 hosts the dual-stack `company.test` web server; and R3 hosts two PCs. IPv4 and IPv6 addressing and routes are static throughout.

Start the lab from this directory with `kathara lstart`.

From the client, verify DNS and HTTP over both address families:

```sh
getent ahostsv4 company.test
getent ahostsv6 company.test
curl -4 http://company.test/
curl -6 http://company.test/
```
