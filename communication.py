import socket
from queue import Queue
import threading

class Communication():
	"""Communication: 
		Handle all communication
	"""

	def __init__(self, from_sock_buff, from_comp_buff, port, frame_size):
		self.input_buffer = from_sock_buff	# data from socket
		self.output_buffer = from_comp_buff	# data to socket
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.port = port	# communication port
		self.conn = None	# connection handler
		self.addr = None
		self.frame_size = frame_size	# socket frame size

	def listen(self):
		"""Wait for connections (server mode)"""
		# get my LAN ip address
		my_ip = Communication.get_ip()

		# wait for connection
		self.s.bind((my_ip, self.port))
		self.s.listen()
		self.conn, self.addr = self.s.accept()

		# start workers
		self.start_proccesses()

	def connect(self, ip_addr):
		"""Connect to user (client mode)"""
		# connect
		self.s.connect((ip_addr, self.port))
		self.conn = self.s

		# start workers
		self.start_proccesses()

	def close(self):
		"""Close connection"""
		if self.s != None:
			self.s.close()
			self.s = None
		if self.conn != None:
			self.conn.close()
			self.conn = None

	def start_proccesses(self):
		"""Start working proccesses"""
		threading.Thread(target=self.receiver, daemon=True).start()
		threading.Thread(target=self.transmmiter, daemon=True).start()


	def receiver(self):
		"""Receive data from socket to queue"""
		print('receiver: start')

		# loop until connection break
		while True:
			data = b''
			# loop until all frame_size arrived from socket
			while len(data) < self.frame_size:
				data += self.conn.recv(self.frame_size - len(data))
				if not data:
					print('receiver: exit')
					return

			# put data into buffer (BLOCKING)
			self.input_buffer.put(data)

	def transmmiter(self):
		"""Receive data from queue and send it to socket"""
		print('transmmiter: start')
		while True:
			# get data from buffer (BLOCKING)
			data = self.output_buffer.get()

			# padd data to frame_size
			if len(data) < self.frame_size:
				data = data + b'\x00' * (self.frame_size - len(data))

			try:
				self.conn.sendall(data)
			except:
				# connection closed
				break

		print('transmmiter: exit')

	def get_ip():
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			# doesn't even have to be reachable
			s.connect(('10.255.255.255', 1))
			IP = s.getsockname()[0]
		except Exception:
			IP = '127.0.0.1'
		finally:
			s.close()
		return IP
		