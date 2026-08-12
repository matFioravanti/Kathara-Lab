# Three-router IPv4 static-routing lab

Start the lab from this directory with `kathara lstart`. The topology is:

`client1, client2 -- router-left -- router-middle -- router-right -- web`

All routing is IPv4 static routing. The web server is `192.168.30.10` and listens on TCP port 80. From either client, verify connectivity with:

```sh
wget -qO- http://192.168.30.10/
```

Addressing:

| Segment | IPv4 network | Addresses |
| --- | --- | --- |
| Client LAN | 192.168.10.0/24 | router-left .1, client1 .11, client2 .12 |
| Left-middle link | 10.0.12.0/30 | router-left .1, router-middle .2 |
| Middle-right link | 10.0.23.0/30 | router-middle .1, router-right .2 |
| Server LAN | 192.168.30.0/24 | router-right .1, web .10 |
