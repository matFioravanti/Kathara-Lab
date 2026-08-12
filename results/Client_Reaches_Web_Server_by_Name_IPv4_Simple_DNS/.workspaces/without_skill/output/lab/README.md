# Authoritative DNS and HTTP lab

Start the lab with `kathara lstart`.  The client (`client`) uses `dns`
(192.168.10.53) as its resolver.  That server is authoritative for
`service.local` and returns 192.168.20.80, the address of `web`.

Verification from the client:

```sh
dig @192.168.10.53 service.local A
getent hosts service.local
curl http://service.local/
```

Both routers use only the static routes in their startup files.  The DNS and
web-server configurations are stored under their respective machine
directories and are installed when each machine starts.
