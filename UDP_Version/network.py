import socket
import pickle
import settings

bufferSize = settings.bufferSize*2

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
            #self.client.connect(self.addr)
            self.client.sendto(str.encode("Hello Server!"), self.addr)
            playerNumber = self.client.recvfrom(bufferSize*2)[0].decode()
            return playerNumber
        except:
            pass

    def send(self, data):
        try:
            self.client.sendto(str.encode(data), self.addr)
            data_encoded = self.client.recvfrom(921781)[0]
            #print("data_encoded: ", data_encoded)
            return pickle.loads(data_encoded)

        except socket.error as e:
            print(e)