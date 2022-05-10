import socket
import pickle
import settings
from _thread import *
from time import sleep
import threading
import os
import subprocess

bufferSize = settings.bufferSize*2

overlayPort = settings.overlayPort

global idGlobalCount

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        #self.client.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, True)
        self.server = settings.serverIP
        self.port = settings.serverPort
        self.addr = (self.server, self.port, 0, 0) #(address, port, flow info, scope id) 4-tuple for AF_INET6)
        self.client.connect(self.addr)
        self.p = -1
        self.canContact = False

    def getP(self):
        return self.p

    def setP(self, p):
        self.p = p

    def connect_network(self):
        try:
            self.client.send(str.encode("Hello Server!"))
            return self.client.recvfrom(bufferSize*2)[0].decode()
        except:
            pass

    #         ret = os.system(f"ping -6 -c 1 -w 1000 -W 1000 {self.server}")

    def tryContact(self):
        try:
            proc = subprocess.Popen(
                ['ping', '-q', '-c', '1', '-w', '1000', '-W', '1000', self.server],
                stdout=subprocess.DEVNULL)
            proc.wait()
            if proc.returncode == 0:
                self.canContact = True
            else:
                self.canContact = False
        except subprocess.error as e:
            print(e)
        return self.canContact

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recvfrom(bufferSize*2)[0])
        except socket.error as e:
            print(e)

    def disconnect_network(self):
        try:
            self.client.send(str.encode("Bye Server!"))
        except:
            pass

    def reconnect_network(self):
        try:
            self.client.send(str.encode("Reconnecting!"))
            self.setP(int(self.client.recvfrom(bufferSize*2)[0].decode()))
            return self.getP()
        except:
            pass