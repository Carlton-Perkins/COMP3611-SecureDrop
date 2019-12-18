#!/usr/bin/env python3

import socket
import struct
import time
import sys
from timeloop import Timeloop
from datetime import timedelta,datetime
from construct import *

ConfinPacket = Struct("key" / Int, "secret" / Int)

# ? Probably should not contain real identification information, should be replace with a negotiation
StringPacket = Struct("name" / CString("utf8"), "id" / VarInt, "confin" / ConfinPacket)
TIMEOUTSIZE = 10

class Peer:
    def __init__(self):
        self.name = str
        self.id = 0
        self.ipaddr = None



# Class to provide a list of peers to the host script
# This class uses a port range to allow for several instances on the same 
# computer to still work

class PeerDetect:
    # Default constructor, name and id need to be defined prior to starting
    def __init__(self, portRange=range(50065, 50075), broadcastGroup='224.3.29.71', id=0, name="Unknown"):
        #Configs
        self.portRange = portRange
        self.broadcastGroup = broadcastGroup
        self.id = id
        self.name = name

        self.DEBUG = False

        #Internals
        self.client = None
        self.server = None
        self.peerList = dict()

    # Send packet via UDP to each port in portRange
    def send(self, message):
        for port in self.portRange:
            self.client.sendto(message, ('224.3.29.71', port))

    # Public method to start both the server and the client
    # Starts timeloop which starts any async functions
    def start(self):
        self._startServer()
        self._startClient()
        
        # timeloop.start(block=False)

    # Internal method to start client
    def _startClient(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.settimeout(0.2)
        ttl = struct.pack('b', 1)
        self.client.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    # Internal method to start server
    def _startServer(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Try binding to all ports, in all ports in port range fail,
        # throw ConnectionError
        connected = False
        for port in self.portRange:
            try:
                self.server.bind(('', port))
                connected = True
                print("Connected with port {}".format(port))
                pass
            except OSError as e:
                print("Can not connect with port {}".format(port))
                pass
            if connected:
                break

        if not connected:
            raise ConnectionError

        group = socket.inet_aton('224.3.29.71')
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.server.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Stop Timeloop
    def stop(self):
        timeloop.stop()

    # Periodic function to check server for messages
    def updateMessages(self):
        data, addr = self.server.recvfrom(1024)
        if data:
            packet = StringPacket.parse(data) # Decode received data

            if not packet.id == self.id:
                if (self.DEBUG): print("Data: {} From: {}".format(packet, addr))

                self.peerList[packet.name] = datetime.now() 

        peerList = self.peerList.copy()
        for peer in peerList:
            if (((datetime.now() - peerList[peer]).seconds) > TIMEOUTSIZE):
                self.peerList.pop(peer)
                print("Peer lost: {}\n".format(peer))

    # Return list of all peers
    def getPeerList(self):
        return self.peerList.copy()

    def setDebug(self, state):
        self.DEBUG = state


# Test function, call with name param as argv
if __name__ == "__main__":

    name = sys.argv[1]
    id = abs(hash(name))

    timeloop = Timeloop()
    peerDetect = PeerDetect(id=id, name=name)

    @timeloop.job(interval=timedelta(seconds=10))
    def broadcast():
        # packet = struct.pack('{}s'.format(len(peerDetect.idPacket)),bytes(peerDetect.idPacket, 'utf-8'))
        s = StringPacket.build(dict(id=peerDetect.id,name=peerDetect.name,confin=dict(key=4,secret=6)))
        peerDetect.send(message=s)

    @timeloop.job(interval=timedelta(seconds=1))
    def receive():
        peerDetect.updateMessages()

    peerDetect.start()    
    while True:
        time.sleep(5)
        pass
