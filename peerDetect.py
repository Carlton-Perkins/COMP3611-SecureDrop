#!/usr/bin/env python3

import socket
import struct
import time
import sys
from timeloop import Timeloop
from datetime import timedelta,datetime
from construct import *

ConfinPacket = Struct("key" / Int, "secret" / Int)
StringPacket = Struct("name" / CString("utf8"), "id" / VarInt, "confin" / ConfinPacket)
TIMEOUTSIZE = 10

class PeerDetect:
    def __init__(self, portRange=range(50065, 50075), broadcastGroup='224.3.29.71', id=-1, name="Unknown"):
        #Configs
        self.portRange = portRange
        self.broadcastGroup = broadcastGroup
        self.id = id
        self.name = name

        #Internals
        self.client = None
        self.server = None
        self.peerList = dict()

    def send(self, message):
        for port in self.portRange:
            self.client.sendto(message, ('224.3.29.71', port))

    def start(self):
        self._startServer()
        self._startClient()
        
        timeloop.start(block=False)

    def _startClient(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.settimeout(0.2)
        ttl = struct.pack('b', 1)
        self.client.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    def _startServer(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

    def stop(self):
        timeloop.stop()

    def updateMessages(self):
        data, addr = self.server.recvfrom(1024)
        if data:
            packet = StringPacket.parse(data)

            if not packet.id == self.id:
                print("Data: {} From: {}".format(packet, addr))

                self.peerList[packet.name] = datetime.now() 

        peerList = self.peerList.copy()
        for peer in peerList:
            if (((datetime.now() - peerList[peer]).seconds) > TIMEOUTSIZE):
                self.peerList.pop(peer)
                print("Client lost: {}".format(peer))

    def getPeerList(self):
        return self.peerList.copy()


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
else:

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

    def startloop():
        timeloop.start(block=False)
    def stoploop():
        timeloop.stop()
