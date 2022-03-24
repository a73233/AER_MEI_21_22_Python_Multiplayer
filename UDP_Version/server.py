import socket
from _thread import *
import pickle
from traceback import print_tb
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

#connected = set()
games = {}
idCount = 0


def threaded_client(msg, addr, p, gameId):
    global idCount

        #while True:
        #try:
            #data = conn.recv(bufferSize*2).decode()
    data = msg

    if gameId in games:
        game = games[gameId]

        if data:   
            if data == "Bye Server!":
                try:
                    del games[gameId]
                    print("Closing Game", gameId)
                except:
                    pass
                idCount -= 1

            elif data == "reset":
                game.resetWent()

            elif data != "get":
                game.play(p, data)

            pickled_data = pickle.dumps(game)
            #print(pickled_data)
            s.sendto(pickled_data, addr)
            #print("just pickled")
            #else:
                #break
        #except:
            #print("Exeception occurred within the threaded_client")
            #break

    #print("Lost connection")
    #try:
    #    del games[gameId]
    #    print("Closing Game", gameId)
    #except:
    #    pass
    #idCount -= 1
    #conn.close()


while True:
    #conn, addr = s.accept()
    msg, addr = s.recvfrom(bufferSize*2)
    msg = msg.decode()
    
    #else:
        #print(msg)

    if (msg == "Hello Server!"):
        print("Connected to:", addr[0], msg)
        idCount += 1
        p = 0
        gameId = (idCount - 1)//2
        if idCount % 2 == 1:
            games[gameId] = Game(gameId)
            print("Creating a new game...")
        else:
            games[gameId].ready = True
            p = 1

        s.sendto(repr(p).encode('utf-8'), addr) #send player number
        continue

    #print("Started a new thread!")
    start_new_thread(threaded_client, (msg, addr, p, gameId))