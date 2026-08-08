# Authoritative DNS and HTTP over static IPv4 routing

This lab demonstrates a client resolving `service.local` through a local authoritative DNS server, then retrieving the corresponding web page from a server on a second LAN. All inter-network routing is static.

## Topology and addressing

| Device | Interface(s) | Addressing / role |
|---|---|---|
| `client` | `eth0` on `LAN_LEFT` | `192.168.10.10/24`; resolver `192.168.10.53` |
| `dns` | `eth0` on `LAN_LEFT` | `192.168.10.53/24`; authoritative for `service.local` |
| `router1` | `eth0` on `LAN_LEFT`, `eth1` on `TRANSIT` | `192.168.10.1/24`, `10.0.0.1/30` |
| `router2` | `eth0` on `TRANSIT`, `eth1` on `LAN_RIGHT` | `10.0.0.2/30`, `192.168.20.1/24` |
| `web` | `eth0` on `LAN_RIGHT` | `192.168.20.10/24`; HTTP server |

The DNS zone maps `service.local` to `192.168.20.10`.

## Run and verify

Start the lab from this directory:

```sh
kathara lstart
```

From the client, resolve the name and fetch the page:

```sh
kathara exec client -- dig service.local
kathara exec client -- curl http://service.local/
```

The DNS answer and HTTP connection both traverse only the statically configured routes.
