# Six-router IPv4 DNS and web laboratory

Run the laboratory with `kathara lstart` from this directory. The `client` host
uses `localdns` (192.168.1.53), which follows a local root hint to `rootdns`.
The root zone delegates `org` to `tlddns`, and the org zone delegates
`research.org` to `authdns`.

On `client`, the intended end-to-end checks are:

```
dig research.org
dig main.research.org
curl http://research.org
curl http://main.research.org
```

Addressing is deliberately separated by function: router LAN interfaces use
192.168.N.1/24, DNS servers use `.53`, servers use `.80`, and client PCs use
`.10` and `.11`. Each router startup file enables forwarding and declares a
static route for every non-directly-connected routed network.
