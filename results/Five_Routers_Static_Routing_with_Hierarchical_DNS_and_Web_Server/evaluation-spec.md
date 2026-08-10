# Scenario requirements

## Network topology

1. The lab contains exactly five routers.
2. Each router has a network degree of at most three.
3. The network uses static routing.

## DNS hierarchy

4. The lab contains three distinct DNS servers with these roles:
   - a root DNS server;
   - an `org` DNS server; and
   - a local name server.
5. The DNS hierarchy provides resolution for the name `kathara.org` to the server that provides that name.

## End-to-end service access

6. The lab contains a server identified by the name `kathara.org`.
7. The lab contains a client that can reach the `kathara.org` server by using the name `kathara.org`.
