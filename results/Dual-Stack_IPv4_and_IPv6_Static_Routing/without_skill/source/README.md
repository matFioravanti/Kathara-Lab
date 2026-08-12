# Dual-stack static routing

This laboratory has two routers joined by a dual-stack point-to-point link. Each router serves a LAN containing two statically addressed PCs. IPv4 and IPv6 forwarding and static routes are configured independently; no dynamic routing protocol or IPv6 address autoconfiguration is used.

## Addressing plan

| Device | Interface | IPv4 address | IPv6 address |
|---|---|---|---|
| r1 | eth0 (left LAN) | 192.168.10.1/24 | 2001:db8:10::1/64 |
| r1 | eth1 (transit) | 10.0.12.1/30 | 2001:db8:12::1/64 |
| r2 | eth0 (transit) | 10.0.12.2/30 | 2001:db8:12::2/64 |
| r2 | eth1 (right LAN) | 192.168.20.1/24 | 2001:db8:20::1/64 |
| pc1 | eth0 | 192.168.10.11/24 | 2001:db8:10::11/64 |
| pc2 | eth0 | 192.168.10.12/24 | 2001:db8:10::12/64 |
| pc3 | eth0 | 192.168.20.11/24 | 2001:db8:20::11/64 |
| pc4 | eth0 | 192.168.20.12/24 | 2001:db8:20::12/64 |

## Verification

After starting the lab, use these commands from `pc1`:

```sh
ping -c 3 192.168.20.11
ping6 -c 3 2001:db8:20::11
```

The equivalent tests can be run between any PC on the left LAN and any PC on the right LAN.
