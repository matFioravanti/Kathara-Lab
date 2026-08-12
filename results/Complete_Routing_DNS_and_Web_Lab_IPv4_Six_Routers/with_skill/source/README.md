# Six-router IPv4 routing and DNS hierarchy

This lab combines a partially meshed six-router IPv4 topology, explicit static routing, and a complete DNS delegation chain. The client on the R1 LAN uses `localdns`; that resolver follows root, `.org`, and `research.org` delegations to resolve the two web services.

Start the lab with `kathara lstart` from this directory. On `client`, verify the exercise with `getent hosts research.org main.research.org`, then run `curl http://research.org` and `curl http://main.research.org`.

## Addressing summary

- Router LAN gateways: `192.168.1.1` through `192.168.6.1`.
- DNS hierarchy: local resolver `192.168.1.53`, root `192.168.2.53`, `.org` TLD `192.168.3.53`, authoritative `192.168.4.53`.
- Web endpoints: `research.org` = `192.168.4.80`; `main.research.org` = `192.168.5.80`.
- Router transit networks: `10.0.12.0/30`, `10.0.13.0/30`, `10.0.24.0/30`, `10.0.25.0/30`, `10.0.35.0/30`, `10.0.46.0/30`, and `10.0.56.0/30`.
