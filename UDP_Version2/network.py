import socket
import pickle
import settings

bufferSize = settings.bufferSize*2

global idGlobalCount

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.server = settings.serverIP
        self.port = settings.serverPort
        self.addr = (self.server, self.port, 0, 0) #(address, port, flow info, scope id) 4-tuple for AF_INET6)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            self.client.send(str.encode("Hello Server!"))
            return self.client.recvfrom(bufferSize*2)[0].decode()
        except:
            pass

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recvfrom(bufferSize*2)[0])
        except socket.error as e:
            print(e)

    def disconnect(self):
        try:
            self.client.send(str.encode("Bye Server!"))
            self.connected = False
        except:
            pass

    def reconnect(self):
        try:
            self.client.connect(self.addr)
            self.client.send(str.encode("Reconnecting!"))
            self.p = self.client.recvfrom(bufferSize*2)[0].decode()
        except:
            pass

    def getPnumber(self):
        return self.p