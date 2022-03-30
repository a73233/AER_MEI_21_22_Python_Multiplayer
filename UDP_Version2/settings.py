from http import client
import socket

serverIP = "::1" # IP DO SERVIDOR , alterar conforme
serverPort = 5555

maxConnections = 1000

bufferSize = 2048