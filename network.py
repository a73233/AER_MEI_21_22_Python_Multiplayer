import socket
import pickle
import settings

bufferSize = settings.bufferSize*2

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        self.server = settings.serverIP
        self.port = settings.serverPort
        self.addr = (self.server, self.port, 0, 0) #(address, port, flow info, scope id) 4-tuple for AF_INET6)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(bufferSize*2).decode()
        except:
            pass

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return pickle.loads(self.client.recv(bufferSize*2))
        except socket.error as e:
            print(e)

