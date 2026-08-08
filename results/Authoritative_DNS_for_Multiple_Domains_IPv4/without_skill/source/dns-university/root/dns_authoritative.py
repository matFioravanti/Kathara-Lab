#!/usr/bin/env python3
"""Minimal authoritative UDP DNS server for one A record."""
import socket
import struct
import sys

DOMAIN, ADDRESS = sys.argv[1].lower(), sys.argv[2]

def question_end(packet):
    offset = 12
    while packet[offset]:
        offset += packet[offset] + 1
    return offset + 5

def qname(packet):
    labels, offset = [], 12
    while packet[offset]:
        n = packet[offset]
        offset += 1
        labels.append(packet[offset:offset+n].decode('ascii', 'ignore'))
        offset += n
    return '.'.join(labels).lower()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 53))
while True:
    query, peer = sock.recvfrom(4096)
    end = question_end(query)
    name = qname(query)
    qtype = struct.unpack('!H', query[end-4:end-2])[0]
    flags = 0x8400 | (int.from_bytes(query[2:4], 'big') & 0x0100)
    answer = b''
    count = 0
    if name == DOMAIN and qtype in (1, 255):
        answer = b'\xc0\x0c' + struct.pack('!HHIH', 1, 1, 300, 4) + socket.inet_aton(ADDRESS)
        count = 1
    elif name != DOMAIN:
        flags |= 3
    header = query[:2] + struct.pack('!H', flags) + struct.pack('!HHHH', 1, count, 0, 0)
    sock.sendto(header + query[12:end] + answer, peer)
