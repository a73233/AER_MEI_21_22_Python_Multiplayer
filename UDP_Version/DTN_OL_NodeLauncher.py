from PIL import Image, ImageTk
import socket, threading, sys, traceback, os

from DTN_OL_Node import DTN_OL_Node

class DTN_OL_NodeLauncher:
	def main(self):
		try:
			self.overlayPort = 1984
			#self.rtspPort = 25000
			#self.rtpPort = 4567
			self.neighbours = []
			for i in range(1, len(sys.argv)):
				self.neighbours.append(sys.argv[i])
		except:
			print("[Usage: DTN_OL_NodeLauncher.py Neighbour1 Neighbour2 etc...]\n")
		#DTN_OL_Node(self.udpPort, self.rtspPort, self.rtpPort, self.neighbours).run()
		DTN_OL_Node(self.overlayPort, self.neighbours).run()
	
if __name__ == "__main__":
	(DTN_OL_NodeLauncher()).main()