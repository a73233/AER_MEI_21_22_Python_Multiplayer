import threading
import socket
import settings
from time import sleep
from threading import Thread

overlayPort = settings.overlayPort
serverIP = settings.serverIP

class DTN_OL_client(Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.cancelled = False

        self.neighAlive = False
        self.aliveNeighLock = threading.Lock()

        self.nextNeigh = None
        self.portBind = ("", overlayPort, 0, 0)
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.portBind)

        self.overlayPort = overlayPort
        self.serverAddrOL = (serverIP, overlayPort, 0, 0)

    def cancel(self):
        self.cancelled = True

    def run(self):
        print("Starting DISCOVER thread...")
        #start_new_thread(self.listenUdp,())
        threading.Thread(target=self.listenUdp).start()

        print("Saying hello to neighbour!")
        self.sendUdp(self.serverAddrOL, "DISCOVER NOIP GO")

        print("Starting HEARTBEAT...") # to discover nodes that have left/crashed
		# ping neighbours every 10 seconds
        #start_new_thread(self.sendHearbeat,())
        threading.Thread(target=self.sendHearbeat).start()


    def sendHearbeat(self):
        while True:
            sleep(10)
            if self.neighAlive == False:
                print("Neighbour",self.serverAddrOL,"is not alive!")
            if self.state == self.TEARDOWN:
                print("Exiting hearbeat thread...")
                break

            self.aliveNeighLock.acquire()
            self.neighAlive = False
            self.aliveNeighLock.release()
            self.sendUdp(self.serverAddrOL, "HEARTBEAT")
    
    def sendUdp(self, neigh, msg):
        sock = self.sock
        sock.sendto(msg.encode('utf-8'), (neigh, self.overlayPort))
        print("Sent", msg, "to", neigh)

    def listenUdp(self):
        sock = self.sock
        print("####### Client is listening #######")
        while True:
            data, address = sock.recvfrom(1024)
            msg = data.decode('utf-8')
            #if self.state == self.TEARDOWN:
            #	break
            print("\n\n Received:", msg, "\n\n")
            msg_list = msg.split(" ")
            
            if msg_list[0] == "HEARTBEAT" and (not self.state == self.TEARDOWN):
                self.sendUdp(address[0], "ACKED_HEARTBEAT")
            elif msg_list[0] == "ACKED_HEARTBEAT":
                #self.aliveNeighLock.acquire()
                self.neighAlive = True
               # self.aliveNeighLock.release()
            elif msg_list[2] == "RETURN":
                if self.nextNeigh is None:
                    self.nextNeigh = address[0]
                    print(self.nextNeigh,"is now my next neighbour")
                    print("Announcing my next neighbour!")
                    self.sendUdp(self.nextNeigh, "ANNOUNCE NOIP")
                
                if len(msg_list) == 3: # é o próprio nó quem mandou o discover
                    print("I sent the DISCOVER myself!")
                else:
                    print("Something went very wrong!")
            else:
                print("2. Something went very wrong!")