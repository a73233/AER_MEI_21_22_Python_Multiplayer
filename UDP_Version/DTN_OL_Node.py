import socket, threading
import threading
from time import sleep
import datetime
import settings

overlayPort = settings.overlayPort

class DTN_OL_Node:

	def __init__(self, overlayport, neighbours):
		self.overlayPort = overlayport
		self.neighbours = neighbours
		
		self.neighboursAlive = [False] * len(self.neighbours)
		self.aliveNeighsLock = threading.Lock()
		
		self.nextNeigh = None
		self.timestampDiscNeigh = []
		self.timeForDiscoveringLastNeigh = datetime.datetime.min
		self.prevTimeForDiscoveringLastNeigh = datetime.datetime.min
		self.reachableClients = []
		self.clientIsPlaying = []
		self.nextNodeToReachClient = []

	def run(self):
		# Find out next neighbour and handle routing
		try:
			self.createUdpSocket()
		except:
			print("Socket Already Binded.")

		self.handleUdpComms()

		print("Starting HEARTBEAT...") # to discover nodes that have left/crashed
		# ping neighbours every 10 seconds
		threading.Thread(target=self.sendHearbeat).start()

	def sendHearbeat(self):
		sizeNeighs = len(self.neighboursAlive)
		neighbours = self.neighbours
		while True:
			sleep(10)
			# ver quais os vizinhos que sairam
			# e dizer q todos os vizinhos sairam
			for i in range(0, sizeNeighs):
				neighIsAlive = self.neighboursAlive[i]
				try:
					neigh = self.neighbours[i]
				except:
					continue

				if neighIsAlive == False:
					print("Neighbour",neigh,"is not alive!")
				self.aliveNeighsLock.acquire()
				self.neighboursAlive[i] = False
				self.aliveNeighsLock.release()
			
			# enviar mensagem para todos os vizinhos
			for neigh in neighbours:
				self.sendUdp(neigh, "HEARTBEAT")


	def getIndexOfClient(self, clientIp):
		rc = self.reachableClients
		for i in range(len(rc)):
			ci = rc[i]
			if ci == clientIp:
				return i
		return -1

	# =============== UDP =========================================================================

	def createUdpSocket(self):
		# UDP Socket
		self.udpSocket = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
		# Bind the socket to the port
		port_address = ("", overlayPort, 0, 0)
		self.udpSocket.bind(port_address)

	def handleUdpComms(self):
		print("Starting DISCOVER thread...") # to discover where to route rtsp packets
		# Create a new thread to listen for UDP packets
		threading.Thread(target=self.listenUdp).start()

		print("Saying hello to neighbours!")
		for neighb in self.neighbours:
			self.timestampDiscNeigh.append(datetime.datetime.now())
			self.sendUdp(neighb, "DISCOVER NOIP GO")
	
	def listenUdp(self):
		sock = self.udpSocket

		print("####### Server is listening #######")
		while True:
			data, address = sock.recvfrom(1024)
			msg = data.decode('utf-8')
			print("\n\n Received:", msg, "\n\n")

			threading.Thread(target=self.processUdpReq, args=(msg, address)).start()

	def processUdpReq(self, msg, address):
		msg_list = msg.split(" ")

		if msg_list[0] == "DISCOVER":
			
			if msg_list[2] == "GO":
			
				excl_neigh = [] # neighbours to not send message!
				
				if msg_list[1] == "NOIP":
					origin_ip = address[0]
				else:
					origin_ip = msg_list[1]
					excl_neigh.append(origin_ip)
					
					for i in range(3, len(msg_list)):
						print(msg_list[i])
						excl_neigh.append(msg_list[i])
				
				print(origin_ip," wants to DISCOVER")
				
				if self.nextNeigh is not None:
					neigh_list = [ self.nextNeigh ]
				else: # preparar lista de vizinhos ao ver a quais vizinhos
						# não vai enviar mensagem
					excl_neigh.append(address[0])

					print("Blacklisted neighbours are:")
					for neigh in excl_neigh:
						print("\t", neigh)
					print("")

					# prepare list of neighbours to send message
					neigh_list = self.neighbours
					for el in excl_neigh:
						if el in neigh_list: 
							neigh_list.remove(el)
				
				# prepare message
				if msg_list[1] == "NOIP":
					msg_list[1] = address[0]
				else:
					msg_list.append(address[0])

				# ver se IP's aparecem duplicados
				# porque se aparecerem, existe um ciclo e
				# a mensagem não é enviada
				msg_set = set(msg_list)
				contains_duplicates = len(msg_set) != len(msg_list)
				if contains_duplicates == True:
					print("msg"," ".join(msg_list),"has duplicates!")
				else:

					new_msg = " ".join(msg_list)

					for el in neigh_list:
						#print("Sending to", el, "msg", new_msg)
						self.sendUdp(el, new_msg)
			
			elif msg_list[2] == "RETURN":
				print("Returning message")
				# ou tem que dar forward para trás
				# ou é o próprio
				# de qualquer forma tem já que saber qual o vizinho usar para o destino

				self.prevTimeForDiscoveringLastNeigh = self.timeForDiscoveringLastNeigh
				ind = 0
				try:
					ind = self.neighbours.index(address[0])
				except ValueError as e:
					print("\t\t*********ERROR: Couldnt find neighbour",src,"!!!!!**********")
					return
				self.timeForDiscoveringLastNeigh = datetime.datetime.now() - self.timestampDiscNeigh[ind] 

				if len(msg_list) == 3: # é o próprio nó quem mandou o discover
					print("I sent the DISCOVER myself!")

					if self.nextNeigh is None:
						self.nextNeigh = address[0]
						print(self.nextNeigh,"is now my next neighbour")
						print("Discovered in",self.timeForDiscoveringLastNeigh,"ms")
					else:
						if self.timeForDiscoveringLastNeigh < self.prevTimeForDiscoveringLastNeigh:
							self.nextNeigh = address[0]
							print(self.nextNeigh,"is now my next neighbour")
							print("Discovered in",self.timeForDiscoveringLastNeigh,"ms")
						else:
							print("Neighbour not altered")
							#print("Assigned neighbour reponse time is",self.prevTimeForDiscoveringLastNeigh,"and now neighbour",address[0],"responded in",self.timeForDiscoveringLastNeigh)
				else:
					msg_list.pop()
					if len(msg_list)==3:
						nodeToSend = msg_list[1]
					else:
						nodeToSend = msg_list[len(msg_list)-1]
					new_msg = " ".join(msg_list)
					#print("Sending",new_msg,"to",nodeToSend)
					self.sendUdp(nodeToSend, new_msg)

		elif msg_list[0] == "ANNOUNCE":
			
			if msg_list[1] == "NOIP": # just received the announce
				msg_list[1] = address[0]
				new_msg = new_msg = " ".join(msg_list)
			else:
				new_msg = msg
			
			if msg_list[1] not in self.reachableClients:
				self.reachableClients.append(msg_list[1])
				self.nextNodeToReachClient.append(address[0])
				self.clientIsPlaying.append(False)
				print("To send packets to client",self.reachableClients[-1],"we must send packet to",address[0])

			self.sendUdp(self.nextNeigh, new_msg)
		
		elif msg_list[0] == "HEARTBEAT":
			self.sendUdp(address[0], "ACKED_HEARTBEAT")
		elif msg_list[0] == "ACKED_HEARTBEAT":
			src = address[0]
			#print("Heartbeat ack came from",src)
			try:
				ind = self.neighbours.index(src)
				self.aliveNeighsLock.acquire()
				self.neighboursAlive[ind] = True
				self.aliveNeighsLock.release()
			except ValueError as e:
				#print("\t\t*********ERROR: Couldnt find neighbour",src,"!!!!!**********")
				print("hcfn\n")

		else:
			print("Unrecognized message received:",msg)

	def sendUdp(self, neigh, msg):
		sock = self.udpSocket
		print("Sent", msg, "to", neigh)
		sock.sendto(msg.encode('utf-8'), (neigh, self.overlayPort))

	# =============== UDP =========================================================================