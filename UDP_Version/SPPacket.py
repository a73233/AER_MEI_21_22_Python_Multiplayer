import sys
from time import time
HEADER_SIZE = 6

class SPPacket:	
	header = bytearray(HEADER_SIZE)
	
	def __init__(self):
		pass
		
	def encode(self, version, padding, extension, cc, marker, payload):
		"""Encode the RTP packet with header fields and payload."""
		timestamp = int(time())
		header = bytearray(HEADER_SIZE) 
		header[0] = (header[0] | version << 6) & 0xC0; # 2 bits
		header[0] = (header[0] | padding << 5); # 1 bit
		header[0] = (header[0] | extension << 4); # 1 bit
		header[0] = (header[0] | (cc & 0x0F)); # 4 bits
		header[1] = (header[1] | marker << 7); # 1 bit

		header[2] = (timestamp >> 24);
		header[3] = (timestamp >> 16) & 0xFF;
		header[4] = (timestamp >> 8) & 0xFF;
		header[5] = (timestamp & 0xFF);

		# set header and  payload
		self.header = header
		self.payload = payload
		
	def decode(self, byteStream):
		"""Decode the SP packet."""
		self.header = bytearray(byteStream[:HEADER_SIZE])
		self.payload = byteStream[HEADER_SIZE:]
	
	def version(self):
		"""Return SP version."""
		return int(self.header[0] >> 6)
	
	
	def timestamp(self):
		"""Return timestamp."""
		timestamp = self.header[2] << 24 | self.header[3] << 16 | self.header[6] << 8 | self.header[7]
		return int(timestamp)
	
	def payloadType(self):
		"""Return payload type."""
		pt = self.header[1] & 127
		return int(pt)
	
	def getPayload(self):
		"""Return payload."""
		return self.payload


	def getPacket(self):
		"""Return SP packet."""
		return self.header + self.payload

	def printheader(self):
		print("[SP Packet] Version: ...")


