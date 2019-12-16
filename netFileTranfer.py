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

if (mode == 'write'):
    conn.bind((ip, port))

    if os.path.exists(file):
        with open(file, 'rb') as f:
            packet = f.read(blocksize)

            while packet != '':
                conn.send(packet)

                packet = f.read(blocksize)
elif (mode == 'read'):
    conn.bind((ip, port))
    conn.listen(10)

    c, addr = conn.accept()
    
    while True:
        data = conn.recv(1024)
        if data: 
            print(data)


