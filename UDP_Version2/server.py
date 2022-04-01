from pydoc import cli
import socket
from _thread import *
import pickle
from threading import Thread
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

    if (data == "Reconnecting!"):
        print("Reconnecting, discarding:", client_addr, data)
        s.sendto(str.encode(str(p)),client_addr)
        players_Hashmap[client_addr] = [p, gameId]
        idCount -= 1

    if (data == "Bye Server!"):
        print("Lost connection:", client_addr, data)
        gameId = players_Hashmap[client_addr][1]

        game = games[gameId]
        game.online = False

        for player_addr in players_Hashmap:
            if players_Hashmap[player_addr][1] == gameId:
                if player_addr != client_addr:
                    s.sendto(pickle.dumps(game), player_addr)
                    #del players_Hashmap[player_addr]
                    #del players_Hashmap[client_addr]
                    #s.sendto(str.encode("Player Left!"), player_addr)
                    #print("Lost connection:", player_addr, data) #tmp
        try:
            #del games[gameId]
            print("Closing Game", gameId)
        except:
            pass
        #idCount = [0, idCount - 2][idCount>0]
        idCount -= 1

    else:
        if gameId in games:
            game = games[gameId]
            game.online = True

            if data:
                if data == "reset":
                    game.resetWent()
                elif data != "get":
                    game.play(p, data)

                s.sendto(pickle.dumps(game),client_addr)



players_Hashmap = {}

while True:
    #conn, addr = s.accept()
    try:
        msg, client_addr = s.recvfrom(bufferSize*2)
        msg = msg.decode()
    except:
        continue

    #Starting Connection
    if (msg == "Hello Server!"):
        #idCount = len(players_Hashmap)
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
        players_Hashmap[client_addr] = [p, gameId]
        continue
    
    start_new_thread(threaded_client, (msg, client_addr, players_Hashmap[client_addr][0], players_Hashmap[client_addr][1]))