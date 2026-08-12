# Client reaches `service.local` over IPv4

## Topology

```
client 192.168.10.10 ─┐                         ┌─ web 192.168.20.20
dns    192.168.10.53 ─┼─ r1 ─ 10.0.0.0/30 ─ r2 ─┤
                      └─ 192.168.10.1     192.168.20.1
```

`dns` is authoritative for `service.local` and returns `192.168.20.20` for
both `service.local` and `web.service.local`. The client uses `192.168.10.53`
as its only resolver. Every non-connected network has an explicit static route.

## Verification

After starting the lab, run these commands in `client`:

```sh
dig service.local A
getent hosts service.local
wget -qO- http://service.local/
```

The DNS answer must be `192.168.20.20`, and the HTTP response contains
`service.local is reachable`.
