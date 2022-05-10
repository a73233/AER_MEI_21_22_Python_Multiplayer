from pydoc import cli
import socket
from _thread import *
import pickle
import threading
from game import Game
import settings
import struct

serverIP = settings.serverIP
serverPort = settings.serverPort
bufferSize = settings.bufferSize
maxConnections = settings.maxConnections
magicNumber = settings.magicNumber
resetCounter = settings.resetCounter

overlayPort=settings.overlayPort

s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

portBind = ("", overlayPort, 0, 0)
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(portBind)

'''
# Allows address to be reused
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Allow messages from this socket to loop back for development
s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_LOOP, True)

# Construct message for joining multicast group
mreq = struct.pack("16s15s".encode('utf-8'), socket.inet_pton(socket.AF_INET6, serverIP), (chr(0) * 16).encode('utf-8'))
s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
'''

try:
    s.bind((serverIP, serverPort, 0, 0))  #(address, port, flow info, scope id) 4-tuple for AF_INET6)
except socket.error as e:
    str(e)

#s.listen(2)
print("UDP Server Started")

connected = set()
games = {}
idCount = 0

def threaded_client(data, client_addr, p, gameId):
    global idCount
    global players_Hashmap

    if (data == "Reconnecting!"):
        print("Reconnecting, discarding:", client_addr, data)
        s.sendto(str.encode(str(p)),client_addr)
        del players_Hashmap[client_addr]
        return

    if (data == "Bye Server!"):
        print("Lost connection:", client_addr, data)
        gameId = players_Hashmap[client_addr][1]
        game = games[gameId]
        game.online = False
        
        for player_addr in players_Hashmap:
            if players_Hashmap[player_addr][1] == gameId:
                if player_addr != client_addr:
                    s.sendto(pickle.dumps(game), player_addr)

        del players_Hashmap[client_addr]
        print("Closing Game", gameId)
        return

    else:
        if gameId in games:
            game = games[gameId]

            if data:
                if data == "reset":
                    game.resetWent()
                elif data != "get":
                    game.play(p, data)

                s.sendto(pickle.dumps(game),client_addr)
                return

def sendUdp(neigh, msg):
    #sock = self.udpSock
    sock.sendto(msg.encode('utf-8'), (neigh, overlayPort))
    print("Sent", msg, "to", neigh)

def listenUdp():
    print("####### Server is listening #######")
    while True:
        data, address = sock.recvfrom(1024)
        msg = data.decode('utf-8')
        print("\n\n Received:", msg,"from",address[0], "\n\n")
        
        msg_list = msg.split(" ")

        if msg_list[0] == "DISCOVER":
            
            if msg_list[2] == "GO":
                msg_list[2] = "RETURN"
                sender_ip = address[0]

                # must add new source
                if msg_list[1] == "NOIP": # one node away from server
                    msg_list[1] = sender_ip
                else: # can be DISCOVER <ip> OR DISCOVER <ip> GO ip2 ip3 ...
                    msg_list.append(sender_ip)
                
                new_msg = " ".join(msg_list)

                print("Message from", sender_ip)
                print("Sending",new_msg,"to",sender_ip)
                sendUdp(sender_ip, new_msg)

players_Hashmap = {}


threading.Thread(target=listenUdp).start()

while True:
    #conn, addr = s.accept()
    try:
        msg, client_addr = s.recvfrom(bufferSize*2)
        msg = msg.decode()
    except:
        continue

    if (msg == "Hello Server!"):
        players_Hashmap_len = len(players_Hashmap)

        if(players_Hashmap_len+1>maxConnections):
            s.sendto(str.encode(str(magicNumber)),client_addr)
            continue

        idCount = idCount%resetCounter + 1
        print("Connected to:", client_addr, msg)
        p = 0
        gameId = (idCount-1)//2

        if idCount%2 == 1:
            games[gameId] = Game(gameId)
            print("Creating a new game...")
        else:
            games[gameId].ready = True
            p = 1

        players_Hashmap[client_addr] = [p, gameId]
        s.sendto(str.encode(str(p)),client_addr)
        continue
    
    #print(idCount, "---" , len(players_Hashmap))
    start_new_thread(threaded_client, (msg, client_addr, players_Hashmap[client_addr][0], players_Hashmap[client_addr][1]))