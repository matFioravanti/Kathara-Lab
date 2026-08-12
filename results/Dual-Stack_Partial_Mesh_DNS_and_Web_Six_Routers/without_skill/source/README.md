# Dual-stack partial mesh DNS and web laboratory

Start the laboratory with `kathara lstart`. Every machine uses its `startup` file, so addressing, forwarding, static routing, DNS zones, and the web service are recreated on each start.

The DNS resolution path is `client -> dns-local -> dns-root -> dns-auth`.  The root server delegates `example.net` to the authoritative server; the authoritative zone supplies A and AAAA records for `example.net` and `www.example.net`.

Useful checks from `client`:

```sh
dig example.net A
dig example.net AAAA
curl -4 http://example.net/
curl -6 http://example.net/
```

All routers and hosts are statically addressed.  IPv4 transit networks use `10.0.XY.0/30`, IPv6 transit networks use `2001:db8:XY::/64`, and LANs use `192.168.N.0/24` and `2001:db8:N::/64`.
