#!/usr/bin/env python3
"""UDP DNS forwarder limited to the two lab domains."""
import socket
import sys

UNIVERSITY, COMPANY = sys.argv[1:3]

def qname(packet):
    labels, offset = [], 12
    while offset < len(packet) and packet[offset]:
        size = packet[offset]
        offset += 1
        labels.append(packet[offset:offset + size].decode('ascii', 'ignore'))
        offset += size
    return '.'.join(labels).lower()

listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
listener.bind(('0.0.0.0', 53))
while True:
    query, client = listener.recvfrom(4096)
    name = qname(query)
    upstream = UNIVERSITY if name.endswith('university.edu') else COMPANY if name.endswith('company.test') else None
    if not upstream:
        flags = int.from_bytes(query[2:4], 'big') | 0x8003
        listener.sendto(query[:2] + flags.to_bytes(2, 'big') + query[4:12] + query[12:], client)
        continue
    relay = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    relay.settimeout(2)
    try:
        relay.sendto(query, (upstream, 53))
        response, _ = relay.recvfrom(4096)
        listener.sendto(response, client)
    except OSError:
        flags = int.from_bytes(query[2:4], 'big') | 0x8002
        listener.sendto(query[:2] + flags.to_bytes(2, 'big') + query[4:12] + query[12:], client)
    finally:
        relay.close()
