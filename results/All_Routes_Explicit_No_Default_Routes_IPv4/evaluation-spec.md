# Kathara Lab Evaluation Specification

## Scope

Design a Kathara lab.

## Devices

- Five routers: R1, R2, R3, R4, and R5.
- Each router serves one LAN.
- Each LAN contains two PCs.
- The lab therefore contains ten PCs in total.

## Router Connectivity

- R1 connects to R2.
- R1 connects to R3.
- R2 connects to R4.
- R3 connects to R4.
- R4 connects to R5.

## Network Protocol

- Use IPv4 only.

## Routing Requirements

- Every router must have a fully explicit routing table.
- Every router must have a specific static route for every remote subnet.
- No router may contain a default route.

## Connectivity Requirement

- All ten PCs must be able to reach each other.

## Unspecified Details

The request does not specify IP addressing, subnet masks or prefixes, interface names, Kathara image selection, collision-domain names, startup-file contents, PC names, or a target lab path.
