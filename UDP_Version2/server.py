import socket
from _thread import *
import pickle
from game import Game
import settings

server = settings.serverIP
port = settings.serverPort
bufferSize = settings.bufferSize

s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

try:
    s.bind((server, port, 0, 0))  #(address, port, flow info, scope id) 4-tuple for AF_INET6)
except socket.error as e:
    str(e)

#s.listen(2)
print("UDP Server Started")

connected = set()
games = {}
idCount = 0


def threaded_client(data, client_addr, p, gameId):
    global idCount

    if gameId in games:
        game = games[gameId]

        if data:
            if data == "reset":
                game.resetWent()
            elif data != "get":
                game.play(p, data)

            s.sendto(pickle.dumps(game),client_addr)

    #print("Lost connection")
    #try:
    #    del games[gameId]
    #    print("Closing Game", gameId)
    #except:
    #    pass
    #idCount -= 1

players_Hashmap = {}

while True:
    #conn, addr = s.accept()
    msg, client_addr = s.recvfrom(bufferSize*2)
    msg = msg.decode()

    if (msg == "Hello Server!"):
        print("Connected to:", client_addr, msg)
        idCount += 1
        p = 0
        gameId = (idCount - 1)//2
        if idCount % 2 == 1:
            games[gameId] = Game(gameId)
            print("Creating a new game...")
        else:
            games[gameId].ready = True
            p = 1

        s.sendto(str.encode(str(p)),client_addr)
        players_Hashmap[client_addr] = p
        continue
    
    start_new_thread(threaded_client, (msg, client_addr, players_Hashmap[client_addr], gameId))