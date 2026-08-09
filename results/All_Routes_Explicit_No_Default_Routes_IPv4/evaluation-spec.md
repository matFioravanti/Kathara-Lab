# Kathara Lab Specification

## Objective

Design a Kathara lab in which all ten PCs can reach one another using IPv4.

## Devices

- Five routers: `R1`, `R2`, `R3`, `R4`, and `R5`.
- Each router serves one LAN.
- Each LAN contains two PCs.
- The lab therefore contains ten PCs in total.

## Required Router Topology

- `R1` connects to `R2`.
- `R1` connects to `R3`.
- `R2` connects to `R4`.
- `R3` connects to `R4`.
- `R4` connects to `R5`.

## Network Protocol

- Use IPv4 only.

## Routing Requirements

- Every router must have a fully explicit routing table.
- On every router, configure a specific static route for every remote subnet.
- Do not configure default routes on any router.

## Connectivity Requirement

- All ten PCs must be able to reach each other.

## Deliberately Unspecified Details

Do not introduce requirements for the following details, which are not specified:

- IP addresses, subnet masks, or an addressing plan.
- Router interface names or interface counts.
- PC names.
- Kathara images.
- Collision-domain names.
- Routing protocols other than the required static routes.
- Services or applications.
- File layout, lab name, or target path.
- Specific validation commands or test destinations.
