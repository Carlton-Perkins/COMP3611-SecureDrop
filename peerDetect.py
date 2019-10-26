#!/usr/bin/env python3

import socket
import struct
import time
from timeloop import Timeloop

portRange = range(50065, 50075)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(0.2)

ttl = struct.pack('b', 1)
client.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

connected = False
for port in portRange:
    try:
        server.bind(('', port))
        connected = True
        print("Connected with port {}".format(port))
        pass
    except OSError as e:
        print("Can not connect with port {}".format(port))
        pass
    if connected:
        break

if not connected:
    exit(-1)

group = socket.inet_aton('224.3.29.71')
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
server.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)



if __name__ == "__main__":
    while True:
        time.sleep(5)

        for port in portRange:
            client.sendto(b'Ping', ('224.3.29.71', port))

        data, addr = server.recvfrom(1024)
        if data:
            print("Data: {} From: {}".format(data, addr))

