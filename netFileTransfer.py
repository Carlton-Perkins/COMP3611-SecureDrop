#!/usr/bin/env python3

import socket
import sys
import os


port = int(sys.argv[1])
ip = sys.argv[2]
file = sys.argv[3]
mode = sys.argv[4]
blocksize = 8192

# print(port + " " + ip + " " + file)

conn = socket.socket()
conn.settimeout(5)

if (mode == 'write'):
    while True:
        conn.connect((ip, port))
        print("loop")

        if os.path.exists(file):
            with open(file, 'rb') as f:
                packet = f.read(blocksize)

                conn.sendall(packet)
                print("Packet done")

                conn.close()
                break
elif (mode == 'read'):
    conn.bind((ip, port))
    conn.listen(10)

    c, addr = conn.accept()
    print('{} connected.'.format(addr))

    while True:
        data = c.recv(blocksize)
        print(data)

        if not data:
            print("Done")
            break
